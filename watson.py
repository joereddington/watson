#!/usr/bin/python
import re
import sys
import math
import pytz
import calendar_helper_functions as icalhelper
import glob
import datetime
import argparse
import os
import json
import timechart
from session import Session
from atom import Atom


#Todo:
# (C) log file to atoms should take content rather than a filename

__TIME_FORMAT = "%d/%m/%y %H:%M"

max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes

def setup_argument_list():
    "creates and parses the argument list for Watson"
    parser = argparse.ArgumentParser( description="manages Watson")
    parser.add_argument("action", help="What to do/display: options are 'sort', 'now', and 'sleep'")
    parser.add_argument('-d', nargs="?" , help="Show only tasks that are at least this many days old")
    parser.add_argument( '-v', dest='verbatim', action='store_true', help='Verbose mode')
    parser.set_defaults(verbatim=False)
    return parser.parse_args()


# Summary ######################################################################

def output_sessions_as_projects(sessions):
        total_time = sum([entry.length()
                          for entry in sessions], datetime.timedelta())
        projects = list(set([entry.project for entry in sessions]))
        for project in projects:
                projectreport(project, sessions, args.verbatim)
        print "Total project time".ljust(45)+str(total_time)
        return total_time


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

def sleep_report(project_sessions):
        for entry in project_sessions:
                        print entry
        total_time = sum([entry.length() for entry in project_sessions], datetime.timedelta())
        average_time = avg_time([entry.length() for entry in project_sessions])
        wake_list = [str(entry.end)[11:] for entry in project_sessions]
#        print wake_list
#        print  mean_time(wake_list)
        st_dev_length = st_dev([entry.length() for entry in project_sessions])
#        print wake_time
        print "\n\nTotal Sleep Time: {}".format(str(total_time)[:-3])
        print "Average Sleep Time: {}".format(str(average_time))
        print "Average Wake Time: {}".format(mean_time(wake_list))
        print "ST-dev for average: {}".format(str(st_dev_length))

        return total_time

from cmath import rect, phase
from math import radians, degrees

def mean_angle(deg):
    return degrees(phase(sum(rect(1, radians(d)) for d in deg)/len(deg)))



def mean_time(times):
    t = (time.split(':') for time in times)
    seconds = ((float(s) + int(m) * 60 + int(h) * 3600)
               for h, m, s in t)
    day = 24 * 60 * 60
    to_angles = [s * 360. / day for s in seconds]
    mean_as_angle = mean_angle(to_angles)
    mean_seconds = mean_as_angle * day / 360.
    if mean_seconds < 0:
        mean_seconds += day
    h, m = divmod(mean_seconds, 3600)
    m, s = divmod(m, 60)
    return '%02i:%02i:%02i' % (h, m, s)


def avg_time(datetimes):
    total = sum(dt.total_seconds() for dt in datetimes)
    avg = total / len(datetimes)
    return datetime.timedelta(seconds=avg);

def st_dev(datetimes):
    total = sum(dt.total_seconds() for dt in datetimes)
    avg = total / len(datetimes)
    #Now for standard devation
    #For each datapoint, find the square of it's difference from the mean and sum them.
    step1 = sum((dt.total_seconds()-avg)*(dt.total_seconds()-avg) for dt in datetimes)
    step2 = step1/len(datetimes)
    step3 = math.sqrt(step2)
    return datetime.timedelta(seconds=step3);


def days_old(session):
        delta = datetime.datetime.now() - session.start
	return delta.days




########## Processing ##########
def get_sessions(atoms):
#This has two phases
        if len(atoms)==0:
            return []
        last= datetime.datetime.strptime( "11/07/10 10:00", __TIME_FORMAT)
        lasttitle=atoms[0].title
        current = atoms[0].get_E()
        grouped_timevalues=[]
        current_group=[]
    #Step1: group all atoms into the largest groups such that every start time but one is within 15 minutes of an end time of another
    #Oh- that's NOT*actually* what this does...this does 'within 15 minutes of the *last*'
        for current in atoms:
                difference=current.get_S()-last

                if ((current.get_S()-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                if (current.get_S() <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                if (current.title != lasttitle): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
		last = current.get_E()
                lasttitle=current.title
                current_group.append(current)
        grouped_timevalues.append(current_group)
        sessions=[]
        #Step 2 - return those groups that are bigger than a set value.
        for i in grouped_timevalues:
            if i:
                if (i[-1].get_E()-i[0].get_S())> datetime.timedelta(minutes=min_session_size):
                    sessions.append(Session(i[0].title,i[0].get_S(),i[-1].get_E(),i))
        return sessions


def get_atom_clusters(atomsin):
    atoms=[]
    lastatom=atomsin[0]
    for atom in atomsin:
        if atom.start[:4]== lastatom.start[:4]:
            atom_minutes=int(atom.start[0:2])*60+int(atom.start[3:5])
            lastatom_minutes=int(lastatom.start[0:2])*60+int(lastatom.start[3:5])
            difference=atom_minutes-lastatom_minutes
            if difference<1:
                atom.title="Exercise"
                atoms.append(atom)
        lastatom=atom
    return atoms

def make_exercise_file(args,atoms):
     sessions=get_sessions(get_atom_clusters(atoms))
     timechart.graph_out(sessions,"exercise")
     return sessions

def make_sleep_file(args,atoms):
     global max_dist_between_logs
     global min_session_size
     pre=max_dist_between_logs
     pre2=min_session_size
     min_session_size = 60  # in minutes
     max_dist_between_logs=240

     sessions=get_sessions(atoms)
     sessions=invert_sessions(sessions)
     max_dist_between_logs=pre
     min_session_size = pre2
     return sessions

def make_projects_file(vision_dir, name):
    atoms=[]
    for file in glob.glob(vision_dir+"/*.md"):
        atoms.extend(log_file_to_atoms(file))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,name)
    return sessions


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


def invert_sessions(sessions):
    lastsession=sessions[0]
    new_sessions=[]
    for session in sessions:
        new_sessions.append(Session(session.project,lastsession.end,session.start,session.content))
        lastsession=session
    return new_sessions


########## Input ##########


def log_file_to_atoms(filename, title=None):
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
        lines=e.split("\n",1)
  #      atom.content="\n".join(lines[1:]).strip()+"\n"
        atom.content=lines[1]
        atom.title=title
        datetitle= e.split("\n")[0]
        date= datetitle.split(",")[0]
        if(len( datetitle.split(","))>1):
            print len(datetitle.split(","))
            postitle= datetitle.split(",")[1]
            if len(postitle)>2:
                atom.title=postitle
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







def heartrate_to_atoms(filename):
    #01-May-2017 23:46,01-May-2017 23:46,69.0
    TF = "%d-%b-%Y %H:%M"
    timestamplength=len("01-May-2017 23:46")
    datelength=len("01-May-2017")
    content=icalhelper.get_content(filename)
    if (args.d):
        if args.d:
            index=int(args.d)*1500
            content=content[len(content)-index:]
    atoms=[]
    for a in content:
        start=a[datelength+1:timestamplength]
        date=a[:datelength]
        end=a[timestamplength+1+datelength+1:(timestamplength*2)+1]
        atoms.append(Atom(start,end,date,"Sleep","Alive",TF))#labeling it sleep is wrong, but it keep the same name for the inversion.
    atoms.pop(0)
    return atoms

def desktop_tracking_file_to_atoms(filename,tag="mail"):
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


def commandline_file_to_atoms(filename):
    filecontent=icalhelper.get_content(filename)
    TF = "%d/%m/%y %H:%M"

    atoms=[]
    for line in filecontent:
        content=line[25:].strip()
        start=line[16:21]
        end=line[16:21]
        date=line[7:9]+"/"+line[10:12]+"/"+line[13:15]
        atoms.append(Atom(start,end,date,"Command line","    "+ content,TF))
    return atoms

    pass


def camera_uploads_to_atoms(targetdir=r"/Users/josephreddington/Dropbox/Camera Uploads/"):
    TF = "%d/%m/%y %H:%M"
    import os.path, time
    atoms=[]
    for file in glob.glob(targetdir+"*"):
        modified_date= datetime.datetime.fromtimestamp(os.path.getmtime(file))
        #content = "\n![Imported Image]({})\n".format(file.replace(" ","\ "))
        content = '\n\n<img alt="Imported Image" src="{}" height=160/></p>\n\n'.format(file)
        atoms.append(Atom(modified_date.strftime("%H:%M"),modified_date.strftime("%H:%M"),modified_date.strftime("%d/%m/%y"),"Image",content,TF))
    return sorted(atoms,key=lambda x: x.get_S(), reverse=False)




# Output

def calendar_output(filename,sessions, matchString=None):
        cal = icalhelper.get_cal()
        for entry in sessions:
            if (matchString==None) or (matchString==entry.project):
                icalhelper.add_event(cal, entry.project, entry.start, entry.end)
        icalhelper.write_cal(filename,cal)


def print_original(atoms):
    for atom in atoms:
        print "###### "+atom.date+ " "+ atom.start+ " to "+atom.end
        print "{}".format(atom.content)


def atoms_to_text(atoms):
    returntext=""
    lastdate=""

    for atom in atoms:
        if lastdate==atom.date:
            datestring=""
        else:
            datestring=" "+atom.date
            lastdate=atom.date
        if atom.start==atom.end:
            returntext+= "######"+datestring+ " "+ atom.start+","
        else:
            returntext+= "######"+datestring+ " "+ atom.start+ " to "+atom.end+","
        returntext+= "{}".format(atom.content)

    return returntext


# Driver files.



def pink_slime(config_file='/config.json'):
  #  print "Hello"
    cwd=os.path.dirname(os.path.abspath(__file__))
    atoms=[]
    atoms.extend(log_file_to_atoms("/Users/josephreddington/Dropbox/git/flow/gromit/journal_2018-01-01.md"))
    atoms.extend(commandline_file_to_atoms(cwd+'/testinputs/commandline.txt'))
    atoms.extend(camera_uploads_to_atoms())
    atoms=cut(atoms,"01-Jan-2018 00:00","01-Jan-2018 23:59")
    temp=sorted(atoms,key=lambda x: x.get_S(), reverse=False)
    sessions=get_sessions(temp)

def full_detect(config_file='/config.json'):
    cwd=os.path.dirname(os.path.abspath(__file__))
    config = json.loads(open(cwd+config_file).read())
    vision_dir = config["projects"]
    gromit_dir = config["journals"]

    if args.action == "now":
	print datetime.datetime.now(pytz.timezone("Europe/London")).strftime("###### "+__TIME_FORMAT)
	return
    sessions=[]
    pacesetter_sessions=get_sessions(log_file_to_atoms(config["pacesetter"]))
    email_sessions=get_sessions(desktop_tracking_file_to_atoms(config["desktop"]))
    watch_atoms=heartrate_to_atoms(config['heart'])
    exercise_sessions=make_exercise_file(args,watch_atoms)
    sleep_sessions=make_sleep_file(args,watch_atoms)
    delores_sessions=get_sessions(log_file_to_atoms(config["delores"]))
    projects_sessions=make_projects_file(vision_dir, "projects")
    gromit_sessions=make_projects_file(gromit_dir, "Journals")
    timechart.graph_out(email_sessions,"email")
    timechart.graph_out(pacesetter_sessions,"Pacesetter")
    timechart.graph_out(delores_sessions,"DELORES")
    timechart.graph_out(gromit_sessions,"journals")

    sessions.extend(pacesetter_sessions)
    sessions.extend(delores_sessions)
    sessions.extend(email_sessions)
    sessions.extend(exercise_sessions)
    sessions.extend(projects_sessions)
    sessions.extend(gromit_sessions)

    if args.d:
            sessions = [i for i in sessions if days_old(i)<int(args.d)]
            sleep_sessions = [i for i in sleep_sessions if days_old(i)<int(args.d)]


    time =0
    if args.action == "sleep":
        time= sleep_report(sleep_sessions)
    else:
       time=  output_sessions_as_projects(sessions)


    calendar_output(cwd+"/calendars/pacesetter.ics",pacesetter_sessions)
    calendar_output(cwd+"/calendars/email.ics",email_sessions)
    calendar_output(cwd+"/calendars/projects.ics",projects_sessions)
    calendar_output(cwd+"/calendars/Exercise.ics",exercise_sessions)
    calendar_output(cwd+"/calendars/Sleep.ics",sleep_sessions)
    return time

