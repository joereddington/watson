#!/usr/bin/python
from __future__ import division
from icalendar import Calendar, Event
import datetime
import argparse
import glob
import os

debug = False
max_dist_between_logs = 15  # in minutes
min_session_size = 15  # in minutes
vision_dir = "/Users/josephreddington/Dropbox/git/Vision/_posts/"
__TIME_FORMAT = "%d/%m/%Y-%H:%M:%S "

def addEvent(cal, summary, start, end, uid):
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', end)
        event['uid'] = summary+str(start)+str(end)
        event.add('priority', 5)

        cal.add_component(event)


class Session(object):
        project = "Unknown"
        start = ""
        end = ""
        content = ""

        def __init__(self, project, start, end, content):
                self.project, self.start, self.end = project, start, end

        def length(self):
                return self.end-self.start

        def __str__(self):
                return "    {} to {} ({})".format(
                    self.start, self.end.time(), self.length())


def setup_argument_list():
        "creates and parses the argument list for naCount"
        parser = argparse.ArgumentParser(description=__doc__)
        parser.add_argument(
            '-v',
            dest='verbatim',
            action='store_true',
         help='Verbose mode')
        parser.set_defaults(verbatim=False)
        parser.add_argument(
            '-d',
            dest='debug',
            action='store_true',
         help='Debugging mode')
        parser.add_argument(
            '-c',
            dest='calendar',
            action='store_true',
         help='Calendar Output')
        parser.set_defaults(debug=False)
        parser.add_argument("action", help='What to show [all/today/graph/calendar]')
        parser.add_argument(
            "target", nargs='?',
            help='displays only files containing this search string.')
        return parser.parse_args()


def process_project_file(fname, sessions):
        with open(fname) as f:
                content = f.readlines()
                sessions.extend(process_content(content, fname))
        return sessions


def get_timevalues(content):
        timestamplines = get_timelines(content)
        #Now remove the Unhelpful timezone from the lines and the #####
        timevalues = [line.split("GMT")[0][7:] for line in timestamplines]
        return timevalues


def get_timelines(content):
        content = [line.replace("BST", "GMT") for line in content]
        content = [line.replace("BST", "GMT") for line in content]
        timestamplines = [line for line in content
                          if "GMT" in line if "#####" in line]
        return timestamplines


def getboundedcontentdic(content):
        boundedcontent = get_timelines(content)
        boundedsessionlines = [
            line for line in boundedcontent
            if "GMT" in line if " to " in line if "#####" in line]
        boundedsessiondic = {}
        for line in boundedsessionlines:
                # print line
                start = line.split("GMT")[0][7:]
                end = line.split(" to ")[1][0:19]

                startts = datetime.datetime.strptime(start, __TIME_FORMAT)
                endts = datetime.datetime.strptime(end+" ", __TIME_FORMAT)
                boundedsessiondic[startts] = endts

        return boundedsessiondic


def process_content(content, fname):
        "Parses content of Vision file, expected to be MarkDown"
        sessions = []
        last = datetime.datetime.strptime(
            "11/07/2010-10:00:06 ", __TIME_FORMAT)
        current = last
        start = 0
        title = fname
        action = ""
        in_session = False
        boundedsessiondic = getboundedcontentdic(content)
        # Find title
        for line in content:
                if "title:" in line:
                        title = line.split(":")[1].strip()
                        break
        # Get the set of times
        timevalues = get_timevalues(content)
        for line in timevalues:
                current = datetime.datetime.strptime(
                        line, __TIME_FORMAT)
                if (in_session):
                        # See if the session should end
                        if ((current-last) > datetime.timedelta(
                                minutes=max_dist_between_logs)):
                                action = "end last at " + \
                                        (str(last))
                                in_session = False
                                # See if the session was long enough to store
                                if ((last-start) > datetime.timedelta(
                                        minutes=min_session_size)):
                                        sessions.append(
                                            Session(title, start, last,content))
                                        # last  is the end of  the session,  but
                                        # current is  the start of  the new one
                                start = current
                                in_session = True
                                action += "and start at "+str(start)
                        else:
                                action = "continue"
                else:
                        start = current
                        in_session = True
                        action = "Start"
                if current in boundedsessiondic:
                        last = boundedsessiondic[current]
                else:
                        last = current
                if (debug):
                        print "Line was {}, action was {}".format(line.strip(), action)
        # If all timestamps have been proceed, and you are still in a session,
        # then end the session.
        if (in_session):
                if ((last-start) > datetime.timedelta(minutes=min_session_size)):
                        sessions.append(Session(title, start, last,content))
        # Now let's look for sessions in the second format. It looks like this:
        # 10/11/2016-11:31:34 GMT to 10/11/2016-11:31:36 GMT:

        return sessions


def projectreport(name, sessions, verbose):
        "Produce report for one project"
        project_sessions = [
            entry for entry in sessions if (
                entry.project == name)]
        total_time = sum([entry.length()
                          for entry in project_sessions], datetime.timedelta())
        if verbose:
                print "#### {}\n\nTotal Time on this project: {}\n".format(name.ljust(45), total_time)
                for entry in project_sessions:
                        print entry
        else:
                print "{}: {}".format(name.ljust(45), total_time)
        return total_time



def day_projects(sessions, today=datetime.datetime.today()):
        single_date_sessions = [
            entry for entry in sessions if (
                entry.start.date() == today.date())]
        total_time = sum(
            [entry.length() for entry in single_date_sessions],
            datetime.timedelta())
        projects = list(
            set([entry.project for entry in single_date_sessions]))
        for project in projects:
                projectreport(
                    project, single_date_sessions, args.verbatim)
        print "### Summary for {}\nTotal project time  -     {}".format(today.date(), total_time)


def all_projects(sessions):
        total_time = sum([entry.length()
                          for entry in sessions], datetime.timedelta())
        projects = list(set([entry.project for entry in sessions]))
        for project in projects:
                projectreport(project, sessions, args.verbatim)
        print "Total project time".ljust(45)+str(total_time)


def calendarreport(name, sessions, verbose):
        "Produce report for one project"
        project_sessions = [
            entry for entry in sessions if (
                entry.project == name)]
        total_time = sum([entry.length()
                          for entry in project_sessions], datetime.timedelta())
        for entry in project_sessions:
                add
        return total_time


def calendar_output(sessions):
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        for entry in sessions:
                addEvent(cal, entry)
        print cal.to_ical()


def addEvent(cal, entry):
        event = Event()
        event.add('summary', entry.project)
        event.add('dtstart', entry.start)
        event.add('dtend', entry.end)
        event.add('dtstamp', entry.end)
        event['uid'] = str(entry).replace(" ", "")
        event.add('priority', 5)

        cal.add_component(event)


#From SE http://stackoverflow.com/questions/13728392/moving-average-or-running-mean

### Running mean/Moving average
def get_running_mean(l, N):
    sum = 0
    result = list( 0 for x in l)

    for i in range( 0, N ):
        sum = sum + l[i]
        result[i] = sum / (i+1)

    for i in range( N, len(l) ):
        sum = sum - l[i-N] + l[i]
        result[i] = sum / N

    return result

def graph_out(sesssions):
        DAY_COUNT = 26
        total_time = []
        for single_date in (
                datetime.datetime.today() - datetime.timedelta(days=n)
                for n in range(DAY_COUNT)):
                single_date_sessions = [
                    entry for entry in sessions if (
                        entry.start.date() == single_date.date())]
                element = int(sum([entry.length(
                        ) for entry in single_date_sessions], datetime.timedelta()).total_seconds()/60)
                total_time = [element]+total_time
        running_mean=get_running_mean(total_time,7)
        print "sessions=["+",".join(str(x) for x in total_time)+"]"
        print "running_mean=["+",".join(str(x) for x in running_mean)+"]"

args = setup_argument_list()
os.chdir(vision_dir)

# sessions=process_project_file(vision_dir+"2017-04-01-tmc50private.md", [])
# This is the line that compiles all of the information.
sessions = process_project_file("/Users/josephreddington/" + "Dropbox/git/DesktopTracking/output/results.txt", [])



if args.action != "calendar":
        if args.action == "graph":
                graph_out(sessions)
        else:
                print "# Project Logs\n"

"""
#### Work Graph
Total Time on this project: 1:43:26

##### Sessions
    2016-08-12 06:16:26 to 06:36:32 (0:20:06)
    2016-08-12 07:58:21 to 09:21:41 (1:23:20)


### Summary for 2016-08-12
Total project time  -     1:43:26"""


if args.action == "today":
        day_projects(sessions)

if args.action == "all":
        all_projects(sessions)

if args.action == "calendar":
        calendar_output(sessions)
