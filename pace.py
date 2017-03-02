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
pacesetter_file="/Users/josephreddington/pacesetter.md"
vision_dir = "/Users/josephreddington/Dropbox/git/Vision/issues/"
os.chdir(vision_dir)

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
                print "#### {}\n\nTotal Time on this project: {}\n".format(name.ljust(45), str(total_time)[:-3])
                for entry in project_sessions:
                        print entry
        else:
                print "{}: {}".format(name.ljust(45), total_time)
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

def get_e(atom):
        total_date=atom['date']+" "+atom['end']
        return datetime.datetime.strptime(total_date,__TIME_FORMAT)


def get_s(atom):
        total_date=atom['date']+" "+atom['start']
        return datetime.datetime.strptime(total_date,__TIME_FORMAT)

def get_sessions(atoms):
        last= datetime.datetime.strptime(
            "11/07/10 10:00", __TIME_FORMAT)
        current = get_e(atoms[0])
        grouped_timevalues=[]
        current_group=[]
        for current in atoms:
                difference=get_s(current)-last
                if ((get_s(current)-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                if (get_s(current) <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                last = get_e(current)
                current_group.append(current)
        grouped_timevalues.append(current_group)
        sessions = []
        for i in grouped_timevalues:
            if i:
                if ((get_e(i[-1])-get_s(i[0]))> datetime.timedelta(minutes=min_session_size)):
                    sessions.append(Session(i[0]['title'],get_s(i[0]),get_e(i[-1]),i))
        return sessions

def read_log_file(filename):
    content=icalhelper.get_content(filename)
    title=filename
    if "title" in content[0]:
        title=content[0][7:]
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
    atoms=read_log_file(pacesetter_file)
    sessions=get_sessions(atoms)
    graph_out(sessions,"pacesetter")
    return sessions


def make_jurgen_file():
    atoms=read_log_file("/Users/josephreddington/Dropbox/git/Vision/jurgen.md")
    sessions=get_sessions(atoms)
    graph_out(sessions,"jurgen")
    return sessions

def make_email_file():
    atoms=read_tracking_file()
    sessions=get_sessions(atoms)
    graph_out(sessions,"email")
    return sessions

def make_projects_file():
    location="/Users/josephreddington/Dropbox/git/Vision/issues/*"
    atoms=[]
    for file in glob.glob(location):
        atoms.extend(read_log_file(file))
    sessions=get_sessions(atoms)
    for session in sessions:
        if "entirely" in session.project:
            print session
    graph_out(sessions,"projects")
    return sessions

def make_project_file(filename):
    atoms=[]
    atoms.extend(read_log_file(filename))
    sessions=get_sessions(atoms)
    graph_out(sessions,"projects")
    return sessions



def read_tracking_file():
    content=icalhelper.get_content('/Users/josephreddington/Dropbox/git/DesktopTracking/output/results.txt')
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

args = setup_argument_list()
sessions=[]
sessions.extend(make_pacesetter_file())
sessions.extend(make_jurgen_file())
sessions.extend(make_email_file())
sessions.extend(make_projects_file())

if args.d:
        sessions = [i for i in sessions if days_old(i)<int(args.d)]

output_sessions_as_projects(sessions)

