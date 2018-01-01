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

import calendar
dict((v,k) for k,v in enumerate(calendar.month_abbr))


def month_string_to_number(string): #from https://stackoverflow.com/a/33736132/170243 (upvoted)
    m = {
        'jan': 1,
        'feb': 2,
        'mar': 3,
        'apr':4,
         'may':5,
         'jun':6,
         'jul':7,
         'aug':8,
         'sep':9,
         'oct':10,
         'nov':11,
         'dec':12
        }
    s = string.strip()[:3].lower()

    try:
        out = m[s]
        return out
    except:
        raise ValueError('Not a month')

def fastStrptime(val, format):
# from http://ze.phyr.us/faster-strptime/
    l = len(val)
    if format == '%d/%m/%y %H:%M' and (l == 14):
        temp= datetime.datetime(
            2000+int(val[6:8]), # %Y
            int(val[3:5]), # %m
            int(val[0:2]), # %d
            int(val[9:11]), # %H
            int(val[12:14]), # %M
            0, # %s
            0, # %f
        )
        return temp
    # The watch
    if format == "%d-%b-%Y %H:%M" and (l == 17):
        temp= datetime.datetime(
            int(val[7:11]), # %Y
            month_string_to_number(val[3:6]), # %m
            int(val[0:2]), # %d
            int(val[12:14]), # %H
            int(val[15:17]), # %M
            0, # %s
            0, # %f
        )
        return temp
    # Default to the native strptime for other formats.
    print "falling through {} {} {}".format(val, format, l)
    return datetime.datetime.strptime(val, format)

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
                self.s= fastStrptime(total_date,self.TF)
                #self.s= datetime.datetime.strptime(total_date,self.TF)
            return self.s

        def get_E(self):
            total_date=self.date+" "+self.end
            types=str(type(self.e))
            if "date" not in types:
                self.e= fastStrptime(total_date,self.TF)
#                self.e= datetime.datetime.strptime(total_date,self.TF)
            #print self.e
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
        return total_time

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


def make_exercise_file(args,watch_file):
     atoms=read_watch_heartrate(watch_file)
     if (args.d):
        if args.d:
            index=int(args.d)*1500
            atoms=atoms[index:]

     atoms=get_atom_clusters(atoms)
     sessions=get_sessions(atoms)
     timechart.graph_out(sessions,"exercise")
     return sessions

def make_sleep_file(args,watch_file):
     global max_dist_between_logs
     global min_session_size
     atoms=read_watch_heartrate(watch_file)
     if (args.d):
        if args.d:
            index=int(args.d)*1500
            atoms=atoms[:index]
     pre=max_dist_between_logs
     pre2=min_session_size
     min_session_size = 60  # in minutes
     max_dist_between_logs=240

     sessions=get_sessions(atoms)
     #for x in sessions:
     #   print x
     sessions=invert_sessions(sessions)
     max_dist_between_logs=pre
     min_session_size = pre2
     return sessions



def make_journal_files():
    atoms=[]
    for file in glob.glob("/home/joereddington/Gromit/*.md"):

        atoms.extend(read_log_file(file))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,"jurgen")
    return sessions


def make_projects_file(vision_dir):
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
    #endsession=sessions[-1]
    #print endsession
    #sessions.append(Session(endsession.project,endsession.start+datetime.timedelta(days=2),endsession.end+datetime.timedelta(days=2),endsession.content))
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

def calendar_output(filename,sessions, matchString=None):
        cal = icalhelper.get_cal()
        for entry in sessions:
            if (matchString==None) or (matchString==entry.project):
                icalhelper.add_event(cal, entry.project, entry.start, entry.end)
        icalhelper.write_cal(filename,cal)



def full_detect(config_file='/config.json'):
    cwd=os.path.dirname(os.path.abspath(__file__))
    config = json.loads(open(cwd+config_file).read())
    vision_dir = cwd+'/../vision/issues/'

    if args.action == "now":
	print datetime.datetime.now(pytz.timezone("Europe/London")).strftime("###### "+__TIME_FORMAT)
	sys.exit()
    sessions=[]
    pacesetter_sessions=make_project_file(config["pacesetter"],"Pacesetter")
    delores_sessions=make_project_file(config["delores"],"DELORES")
    email_sessions=make_email_file(config["desktop"])
    projects_sessions=make_projects_file(vision_dir)
    exercise_sessions=make_exercise_file(args,config["heart"])
    sleep_sessions=make_sleep_file(args,config["heart"])

    sessions.extend(pacesetter_sessions)
    sessions.extend(delores_sessions)
    sessions.extend(email_sessions)
    sessions.extend(exercise_sessions)
    sessions.extend(projects_sessions)

    calendar_output(cwd+"/calendars/pacesetter.ics",pacesetter_sessions)
    calendar_output(cwd+"/calendars/email.ics",email_sessions)
    calendar_output(cwd+"/calendars/projects.ics",projects_sessions)
    calendar_output(cwd+"/calendars/Exercise.ics",exercise_sessions)
    calendar_output(cwd+"/calendars/Sleep.ics",sleep_sessions)
    if args.d:
            sessions = [i for i in sessions if days_old(i)<int(args.d)]
            sleep_sessions = [i for i in sleep_sessions if days_old(i)<int(args.d)]



    if args.action == "sleep":
        return output_sessions_as_projects(sleep_sessions)
    else:
       return  output_sessions_as_projects(sessions)




