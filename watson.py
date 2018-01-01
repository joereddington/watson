#!/usr/bin/python
import re
import sys
import traceback
import pytz
import calendar_helper_functions as icalhelper
import glob
import sys
import time
import datetime
import argparse
import os
import json
import timechart

__TIME_FORMAT = "%d/%m/%y %H:%M"

max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes
config = json.loads(open(os.path.dirname(os.path.abspath(__file__))+'/config.json').read())
vision_dir = os.path.dirname(os.path.abspath(__file__))+'/../vision/issues/'

pacesetter_file = os.path.dirname(os.path.abspath(__file__))+'/../../pacesetter.md'
watch_file=config["heart"]
delores_file=config["delores"]
pacesetter_file=config["pacesetter"]
jurgen_file=config["livenotes"]
email_file = config["desktop"]

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

class Atom(object):

        def __init__(self, start="",end="", date="",title="", content="", TF="%d/%m/%y %H:%M"):
            self.content=start
            self.start=end
            self.title=title
            self.end=end
            self.date=date
            self.TF=TF
            self.s=0
            self.e=0

        def get_S(self):
            total_date=self.date+" "+self.start
            types=str(type(self.s))
            if "date" not in types:
                self.s= datetime.datetime.strptime(total_date,self.TF)
            return self.s

        def get_E(self):
            total_date=self.date+" "+self.end
            types=str(type(self.e))
            if "date" not in types:
                self.e= datetime.datetime.strptime(total_date,self.TF)
            return self.e

        def __str__(self):
            return "{}, from {} to {} on {}".format(self.title,self.start,self.end,self.date)


def setup_argument_list():
    "creates and parses the argument list for Watson"
    parser = argparse.ArgumentParser( description="manages Watson")
    parser.add_argument("action", help="What to do/display: options are 'graph', 'info', and 'calendar'")
    parser.add_argument('-c', nargs="?", help="if context_filter is activated then only actions in the relevant contexts (contexts are generally in 'bgthop0ry') are counted")
    parser.add_argument('-d', nargs="?" , help="Show only tasks that are at least this many days old")
    parser.add_argument( '-n', nargs="?", help="reverse context filter, eliminates certain contexts from the count")
    parser.add_argument( '-s', action='store_true', help="use if called by a script or cron")
    parser.add_argument( '-v', dest='verbatim', action='store_true', help='Verbose mode')
    parser.add_argument( '-e', dest='excelmode', action='store_true', help='Output for excel')
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

def get_sessions(atoms):
        last= datetime.datetime.strptime( "11/07/10 10:00", __TIME_FORMAT)
        current = atoms[0].get_E()
        grouped_timevalues=[]
        current_group=[]
        for current in atoms:
                difference=current.get_S()-last
                if ((current.get_S()-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                if (current.get_S() <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
		last = current.get_E()
                current_group.append(current)
        grouped_timevalues.append(current_group)
        sessions = []
        for i in grouped_timevalues:
            if i:
                if (i[-1].get_E()-i[0].get_S())> datetime.timedelta(minutes=min_session_size):
                    sessions.append(Session(i[0].title,i[0].get_S(),i[-1].get_E(),i))
        return sessions

def read_log_file(filename, title=None):
    if title==None:
	title=filename
    content=icalhelper.get_content(filename)
    if "title" in content[0]:
        title=content[0][7:].strip()
    entries="\n".join(content).split("######")
    atoms=[]
    lastdate="01/01/10"
    date=""
    entries=entries[1:]
    for e in entries:
        atom=Atom()
        lines=e.split("\n")
        atom.content="\n".join(lines[1:]).strip()+"\n"
        atom.title=title
        date= e.split("\n")[0]
        date=date.replace("2016-","16 ")
        date=date.replace("2017-","17 ")
        date=re.sub(r":[0-9][0-9] GMT","",date)
        date=re.sub(r":[0-9][0-9] BST","",date)
        date=re.sub(r"to [0-9][0-9]/../..","to",date)
        if date.find("/")>0: #Then we have both date and time.
            newdate=date[:9].strip()
            atom.start=date[9:9+15].strip()
            atom.date=newdate
            lastdate=newdate
        else:
            atom.start=date.strip()
            atom.date=lastdate
        if "to" in atom.start:
            #Then it was a 'to' construct and has a start and end time
            atom.end = atom.start[9:]
            atom.start = atom.start[:5]
        else:
            atom.end=atom.start
        atom.start=atom.start[:5]
        atom.end=atom.end[:5]
        atoms.append(atom)

    return atoms


def read_watch_heartrate(filename):
    #01-May-2017 23:46,01-May-2017 23:46,69.0
    TF = "%d-%b-%Y %H:%M"
    timestamplength=len("01-May-2017 23:46")
    datelength=len("01-May-2017")
    content=icalhelper.get_content(filename)
    atoms=[]
    for a in content:
        start=a[datelength+1:timestamplength]
        date=a[:datelength]
        end=a[timestamplength+1+datelength+1:(timestamplength*2)+1]
        atoms.append(Atom(start,end,date,"Heartrate","Alive",TF))
    atoms.pop(0)
    return atoms


def get_atom_clusters(atomsin):
    atoms=[]
    lastatom=atomsin[0]
    for atom in atomsin:
        if atom.start[:4]== lastatom.start[:4]:
            difference=atom.get_S()-lastatom.get_S()
            if difference<datetime.timedelta(minutes=1):
                atom.title="Exercise"
                atoms.append(atom)
        lastatom=atom
    return atoms
# From SE
# http://stackoverflow.com/questions/13728392/moving-average-or-running-mean


def make_project_file(filename,name):
    atoms=[]
    atoms.extend(read_log_file(filename))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,name)
    return sessions

def make_email_file(filename):
    atoms=read_tracking_file(filename)
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,"email")
    return sessions


def make_exercise_file(args):
     atoms=read_watch_heartrate(watch_file)
     if (args.d):
        if args.d:
            index=int(args.d)*1500
            atoms=atoms[index:]

     atoms=get_atom_clusters(atoms)
     sessions=get_sessions(atoms)
     timechart.graph_out(sessions,"exercise")
     return sessions

def make_sleep_file(args):
     global max_dist_between_logs
     global min_session_size
     atoms=read_watch_heartrate(watch_file)
     if (args.d):
        if args.d:
            index=int(args.d)*1500
            atoms=atoms[:index]
     pre=max_dist_between_logs
     pre2=min_session_size
     min_session_size = 240  # in minutes
     max_dist_between_logs=240

     sessions=get_sessions(atoms)

     sessions=invert_sessions(sessions)
     max_dist_between_logs=pre
     min_session_size = pre2
     return sessions



def make_journal_files():
    atoms=[]
    for file in glob.glob("/home/joereddington/Gromit/*.md"):
	#print file
        atoms.extend(read_log_file(file))
    atoms.extend(read_log_file(jurgen_file))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,"jurgen")
    return sessions


def make_projects_file():
    atoms=[]
    for file in glob.glob(vision_dir+"/*.md"):
	#print file
        atoms.extend(read_log_file(file))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,"projects")
    return sessions

def read_tracking_file(filename,tag="mail"):
    content=icalhelper.get_content(filename)
    matchingcontent= [line for line in content if (tag in line )]
    TF = "%d/%m/%y %H:%M"

    atoms=[]
    for line in matchingcontent:
        content=line[19:]
        start=line[11:16]
        end=line[11:16]
        date=line[8:10]+"/"+line[5:7]+"/"+line[2:4]
        atoms.append(Atom(start,end,date,"mail",content,TF))
    return atoms


def days_old(session):
        delta = datetime.datetime.now() - session.start
	return delta.days

def invert_sessions(sessions):
    lastsession=sessions[0]
    new_sessions=[]
    for session in sessions:
        new_sessions.append(Session(session.project,lastsession.end,session.start,session.content))
        lastsession=session
    return new_sessions


def cut(atoms,start,end):
    TF = "%d-%b-%Y %H:%M"
    start_time= datetime.datetime.strptime( start, TF)
    end_time= datetime.datetime.strptime( end, TF)
    return_atoms=[]
    for current in atoms:
            if (current.get_S() > start_time):
                if (current.get_S() < end_time):
                    return_atoms.append(current)
    return return_atoms




def calendar_output(filename,sessions):
        cal = icalhelper.get_cal()
        for entry in sessions:
                icalhelper.add_event(cal, entry.project, entry.start, entry.end)
        icalhelper.write_cal(filename,cal)


def full_detect():
    if args.action == "now":
	print datetime.datetime.now(pytz.timezone("Europe/London")).strftime("###### "+__TIME_FORMAT)
	sys.exit()
    sessions=[]
    pacesetter_sessions=make_project_file(pacesetter_file,"Pacesetter") 
    jurgen_sessions=make_journal_files()
    delores_sessions=make_project_file(delores_file,"DELORES") 
    email_sessions=make_email_file(email_file) 
    projects_sessions=make_projects_file() 
    exercise_sessions=make_exercise_file(args)
    sleep_sessions=make_sleep_file(args)
    sessions.extend(pacesetter_sessions)
    sessions.extend(jurgen_sessions)
    sessions.extend(delores_sessions)
    sessions.extend(email_sessions)
    sessions.extend(exercise_sessions)
    sessions.extend(projects_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/pacesetter.ics",pacesetter_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/jurgen.ics",jurgen_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/jurgen.ics",jurgen_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/email.ics",email_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/projects.ics",projects_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/Exercise.ics",exercise_sessions)
    calendar_output(os.path.dirname(os.path.abspath(__file__))+"/calendars/Sleep.ics",sleep_sessions)
    if args.d:
            sessions = [i for i in sessions if days_old(i)<int(args.d)]
            sleep_sessions = [i for i in sleep_sessions if days_old(i)<int(args.d)]



    if args.action == "sleep":
        output_sessions_as_projects(sleep_sessions)
    else:
        output_sessions_as_projects(sessions)

def mrslandingham_detect():
    sessions=make_project_file("../mrslandingham/log_files/ml_log_desktop.md","Mrs Landingham")
    sessions = [i for i in sessions if days_old(i)<int(args.d)]
    output_sessions_as_projects(sessions)


