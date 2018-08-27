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
    parser.add_argument('-d', nargs="?" , help="Show only tasks that are at least this many days old")
    parser.set_defaults(verbatim=False)
    return parser.parse_args()


def output_sessions_as_account(sessions):
        total_time = sum([entry.length()
                          for entry in sessions], datetime.timedelta())
        projects = {}
        for session in sessions:
            if session.project in projects:
               projects[session.project]+=session.length()
            else:
               projects[session.project]=session.length()

        for key, value in sorted(projects.iteritems(), key=lambda (k,v): (v,k)):
            print "%s: %s" % (value, key)


        print "Total project time".ljust(45)+str(total_time)
        return total_time


def days_old(session):
        delta = datetime.datetime.now() - session.start.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
	return delta.days

########## Processing ##########
def get_sessions(atoms):
#This has two phases
        if len(atoms)==0:
            return []
        last= datetime.datetime.strptime( "11/07/10 10:00", __TIME_FORMAT)
        lasttitle=atoms[0].title
        current = atoms[0].get_S()
        grouped_timevalues=[]
        current_group=[]
    #Step1: group all atoms into the largest groups such that every start time but one is within 15 minutes of an end time of another
    #Oh- that's NOT*actually* what this does...this does 'within 15 minutes of the *last*'
        for current in atoms:
                if ((current.get_S()-last) > datetime.timedelta( minutes=max_dist_between_logs)):
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                elif (current.get_S() <last): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
                elif (current.title != lasttitle): #preventing negative times being approved...
                    grouped_timevalues.append(current_group)
                    current_group=[current]
		last = current.get_E()
                lasttitle=current.title
                current_group.append(current)
        grouped_timevalues.append(current_group)
        #Step 2 - return those groups that are bigger than a set value.
        sessions=[]
        for i in grouped_timevalues:
            if i:
                if ((get_latest_end(i)-get_earliest_start(i)) >datetime.timedelta(minutes=min_session_size)):
                    sessions.append(Session(i[0].title,get_earliest_start(i),get_latest_end(i),i))
        return sessions


def get_latest_end(atoms):
    max=atoms[0].get_E()
    for atom in atoms:
        if atom.get_E()>max:
            max=atom.get_E()
    return max


def get_earliest_start(atoms):
    min=atoms[0].get_S()
    for atom in atoms:
        if atom.get_S()<min:
            min=atom.get_E()
    return min

def make_projects_file(vision_dir, name):
    atoms=[]
    for file in glob.glob(vision_dir+"/*.md"):
        atoms.extend(log_file_to_atoms(file))
    sessions=get_sessions(atoms)
    timechart.graph_out(sessions,name)
    return sessions



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

def full_detect(config_file='/config.json'):
    cwd=os.path.dirname(os.path.abspath(__file__))
    config = json.loads(open(cwd+config_file).read())
    gromit_dir = config["journals"]

    sessions=make_projects_file(gromit_dir, "Journals")
    if args.d:
            sessions = [i for i in sessions if days_old(i)<int(args.d)]
    output_sessions_as_account(sessions)

