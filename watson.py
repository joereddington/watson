#!/usr/bin/python
import re
import calendar_helper_functions as icalhelper
import glob
import time
import datetime
import argparse
import os

__TIME_FORMAT = "%d/%m/%y %H:%M"

max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes
vision_dir = os.path.dirname(os.path.abspath(__file__))+'/../vision/issues/'
pacesetter_file = os.path.dirname(os.path.abspath(__file__))+'/pacesetter.md'
email_file = os.path.dirname(os.path.abspath(__file__))+'/../../desktop.md'

class Session(object):
        project = "Unknown"
        start = ""
        end = ""
        content = ""

        def __init__(self, project, start, end, content):
                self.project, self.start, self.end = project, start, end

        def length(self):
                return (self.end-self.start)

        def __str__(self):
                return "    {} to {} ({})".format(
                    self.start.strftime("%d/%m/%y %H:%M"), self.end.strftime("%H:%M"), str(self.length())[:-3])


def setup_argument_list():
    "creates and parses the argument list for Watson"
    parser = argparse.ArgumentParser(
        description="manages Watson")
    parser.add_argument("action", help="What to do/display: options are 'graph', 'info', and 'calendar'")
    parser.add_argument('-c', nargs="?", help="if context_filter is activated then only actions in the relevant contexts (contexts are generally in 'bgthop0ry') are counted")
    parser.add_argument('-d', nargs="?" , help="Show only tasks that are at least this many days old")
    parser.add_argument( '-n', nargs="?", help="reverse context filter, eliminates certain contexts from the count")
    parser.add_argument( '-s', action='store_true', help="use if called by a script or cron")
    parser.add_argument( '-v', dest='verbatim', action='store_true', help='Verbose mode')
    parser.add_argument( "target", nargs='?', help='displays only files containing this search string.')
    parser.set_defaults(verbatim=False)
    return parser.parse_args()


def projectreport(name, sessions, verbose):
        project_sessions = [ entry for entry in sessions if ( entry.project == name)]
        total_time = sum([entry.length() for entry in project_sessions], datetime.timedelta())
        if verbose:
                print "#### {}\n\nTotal Time on this project: {}\n".format(name.strip().ljust(65), str(total_time)[:-3])
                for entry in project_sessions:
                        print entry
        else:
                print "{}: {}".format(name.strip().ljust(45), total_time)
        return total_time


def print_original(atoms):
    previous_date=""
    for atom in atoms:
      if atom['date']==previous_date:
        print "###### "+atom['start']+ "Where is the end time???"
      else:
        print "###### "+atom['date']+ " "+ atom['start']+ "Where is the end time???"
        previous_date=atom['date']
      print atom['content']
      print "____________________________________________________________________________"

def output_sessions_as_projects(sessions):
        total_time = sum([entry.length()
                          for entry in sessions], datetime.timedelta())
        projects = list(set([entry.project for entry in sessions]))
        for project in projects:
                projectreport(project, sessions, args.verbatim)
        print "Total project time".ljust(45)+str(total_time)

def get_e(atom,TF):
        total_date=atom['date']+" "+atom['end']
	try:
		returnvalue= datetime.datetime.strptime(total_date,TF)
		return returnvalue
	except ValueError:
		print "Value error!"
		print total_date
		return 0


def get_s(atom,TF):
        total_date=atom['date']+" "+atom['start']
        return datetime.datetime.strptime(total_date,TF)

def get_sessions(atoms,TF=__TIME_FORMAT):
        last= datetime.datetime.strptime( "11/07/10 10:00", __TIME_FORMAT)
        current = get_e(atoms[0],TF)
        grouped_timevalues=[]
        current_group=[]
        for current in atoms:
                difference=get_s(current,TF)-last
                if ((get_s(current,TF)-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                if (get_s(current,TF) <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                last = get_e(current,TF)
                current_group.append(current)
        grouped_timevalues.append(current_group)
        sessions = []
        for i in grouped_timevalues:
            if i:
                if ((get_e(i[-1],TF)-get_s(i[0],TF))> datetime.timedelta(minutes=min_session_size)):
#                    print "{} {} {}".format(i[0]['title'],get_s(i[0]),get_e(i[-1]),i)
                    sessions.append(Session(i[0]['title'],get_s(i[0],TF),get_e(i[-1],TF),i))
        return sessions

def read_log_file(filename, title=None):
    if title==None:
	title=filename
    content=icalhelper.get_content(filename)
    if "title" in content[0]:
        title=content[0][7:].strip()
    entries="\n".join(content).split("######")
    atoms=[]
    atom={}
    lastdate="01/01/10"
    date=""
    entries=entries[1:]
    for e in entries:
        lines=e.split("\n")
        atom['content']="\n".join(lines[1:]).strip()+"\n"
        atom['start']=""
        atom['title']=title
        date= e.split("\n")[0]
        date=date.replace("2016-","16 ")
        date=date.replace("2017-","17 ")
        date=re.sub(r":[0-9][0-9] GMT","",date)
        date=re.sub(r":[0-9][0-9] BST","",date)
        date=re.sub(r"to [0-9][0-9]/../..","to",date)
        if date.find("/")>0: #Then we have both date and time.
            newdate=date[:9].strip()
            atom['start']=date[9:len(date)].strip()
            atom['date']=newdate
            lastdate=newdate
        else:
            atom['start']=date.strip()
            atom['date']=lastdate
        if len(atom['start'])>6:
            #Then it was a 'to' construct and has a start and end time
            atom['end'] = atom['start'][9:]
            atom['start'] = atom['start'][:5]
        else:
            atom['end']=atom['start']
        atom['start']=atom['start'][:5]
        atom['end']=atom['end'][:5]
        atoms.append(atom.copy())

    previous_date=""
    return atoms


def read_watch_heartrate(filename):
    #01-May-2017 23:46,01-May-2017 23:46,69.0
    timestamplength=len("01-May-2017 23:46")
    datelength=len("01-May-2017")
    content=icalhelper.get_content(filename)
    atoms=[]
    atom={}
    atom['content']="alive"
    atom['title']="Heartrate"
#    content.pop(0)#remove header low.
    for a in content:
        start=a[datelength+1:timestamplength]
        date=a[:datelength]
        end=a[timestamplength+1+datelength+1:(timestamplength*2)+1]
        atom['start']=start
        atom['end']=end
        atom['date']=date
        atoms.append(atom.copy())
      #  print "X{}X to Z{}Z on Y{}Y".format(start, end,date)
    return atoms

# From SE
# http://stackoverflow.com/questions/13728392/moving-average-or-running-mean

# Running mean/Moving average
def get_running_mean(l, N):
        sum = 0
        result = list(0 for x in l)

        for i in range(0, N):
                sum = sum + l[i]
                result[i] = sum / (i+1)

        for i in range(N, len(l)):
                sum = sum - l[i-N] + l[i]
                result[i] = sum / N

        return result

def make_pacesetter_file():
    atoms=read_log_file(pacesetter_file, "Pacesetter")
    sessions=get_sessions(atoms)
    graph_out(sessions,"pacesetter")
    return sessions


def make_jurgen_file():
    atoms=read_log_file(os.path.dirname(os.path.abspath(__file__))+'/../vision/jurgen.md')
    sessions=get_sessions(atoms)
    graph_out(sessions,"jurgen")
    return sessions

def make_email_file():
    atoms=read_tracking_file()
    sessions=get_sessions(atoms)
    graph_out(sessions,"email")
    return sessions

def make_projects_file():
    atoms=[]
    for file in glob.glob(vision_dir+"/*.md"):
        atoms.extend(read_log_file(file))
    sessions=get_sessions(atoms)
    #for session in sessions:
#        if "entirely" in session.project:
#            print session
    graph_out(sessions,"projects")
    return sessions

def make_project_file(filename):
    atoms=[]
    atoms.extend(read_log_file(filename))
    sessions=get_sessions(atoms)
    graph_out(sessions,"projects")
    return sessions



def read_tracking_file():
    content=icalhelper.get_content(email_file)
    matchingcontent=  [line for line in content if ("mail" in line )]
    atoms=[]
    for line in matchingcontent:
        atom={}
        atom['content']=line[19:]
        atom['start']=line[11:16]
        atom['title']="mail"
        atom['end']=line[11:16]
        atom['date']=line[8:10]+"/"+line[5:7]+"/"+line[2:4]
        atoms.append(atom.copy())
    return atoms



def graph_out(sessions,slug):
        DAY_COUNT = 26
        total_time = []
        for single_date in (
                datetime.datetime.today() - datetime.timedelta(days=n)
                for n in range(DAY_COUNT)):
                single_date_sessions = [
                    entry for entry in sessions if (
                        entry.start.date() == single_date.date())]
                element = int(
                              sum(
                                  [entry.length()
                                   for entry in single_date_sessions],
                                  datetime.timedelta()).total_seconds() / 60)
                total_time = [element]+total_time
        running_mean = get_running_mean(total_time, 7)
        write_to_javascript(total_time,running_mean,slug)

def days_old(session):
        delta = datetime.datetime.now() - session.start
	return delta.days

def write_to_javascript(total_time,running_mean,slug):
        f = open(vision_dir+"../../watson/javascript/"+slug+".js", 'wb')
        f.write(slug+"sessions=["+",".join(str(x) for x in total_time)+"];\n")
        f.write(slug+"running_mean=["+",".join(str(x) for x in running_mean)+"]")
        f.close()




#args = setup_argument_list()


def invert_sessions(sessions):
    lastsession=sessions[0]
    new_sessions=[]
    for session in sessions:
        final= lastsession.end
        new_sessions.append(Session(session.project,final,session.start,session.content))
        lastsession=session
    return new_sessions


def calendar_output(filename,sessions):
        cal = icalhelper.get_cal()
        for entry in sessions:
                icalhelper.add_event(cal, entry.project, entry.start, entry.end)
        icalhelper.write_cal(filename,cal)



def sleep():
     TF = "%d-%b-%Y %H:%M"
     global max_dist_between_logs
     pre=max_dist_between_logs
     pre2=min_session_size = 15  # in minutes
     min_session_size = 240  # in minutes
     max_dist_between_logs=240
     atoms=read_watch_heartrate("/Users/josephreddington/Dropbox/Heart Rate.csv")
     atoms.pop(0) #to get rid of the column titles
     sessions=get_sessions(atoms,TF)
     sessions=invert_sessions(sessions)
     max_dist_between_logs=pre
     min_session_size = pre2
     print sessions
     projects = list(set([entry.project for entry in sessions]))
     for project in projects:
             projectreport(project, sessions, True)
     calendar_output(os.path.dirname(os.path.abspath(__file__))+"/Sleep.ics",sessions)



def do():

  if args.action == "sleep":
        sleep()
  else:
    sessions=[]
    pacesetter_sessions=make_pacesetter_file()
    jurgen_sessions=make_jurgen_file()
    email_sessions=make_email_file()
    projects_sessions=make_projects_file()
    sessions.extend(pacesetter_sessions)
    sessions.extend(jurgen_sessions)
    sessions.extend(email_sessions)
    sessions.extend(projects_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/pacesetter.ics",pacesetter_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/jurgen.ics",jurgen_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/email.ics",email_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/projects.ics",projects_sessions)
    if args.d:
            sessions = [i for i in sessions if days_old(i)<int(args.d)]

    output_sessions_as_projects(sessions)

