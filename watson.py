#!/usr/bin/python
import re
import sys
import math
import pytz
import glob
import datetime
import argparse
import os
import json
import timechart
from entry import Entry



def get_content(infilename):
        with open(infilename) as f:
                content = f.readlines()
        return content



# Whole new THING

def propagate_dates(entries):
    current_date=None
    for entry in entries:
        if entry.date!=None:
            current_date=entry.date
        entry.date=current_date


def propagate_endings(entries,max_minutes):
    laststart=None
    for entry in reversed(entries):
        if entry.end==None:
            entry.end=laststart
            if entry.get_duration()>max_minutes:
                entry.end=None
        laststart=entry.start

def total_duration(entries,matchtext=""):
    running_total=0
    for entry in entries:
        if matchtext in entry.title:
            running_total+=entry.get_duration()
    return running_total



#Todo:
# (C) log file to atoms should take content rather than a filename

__TIME_FORMAT = "%d/%m/%y %H:%M"

max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes

def setup_argument_list():
    "creates and parses the argument list for Watson"
    parser = argparse.ArgumentParser( description="manages Watson")
    parser.add_argument('filename')
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
        delta = datetime.datetime.now() - session.date.replace(hour = 0, minute = 0, second = 0, microsecond = 0)
	return delta.days

def report_on_day(file):
    print file
    entries=[]
    content=get_content(file)
    for line in content:
        if "###" in line:
            entries.append(Entry(line))
    propagate_dates(entries)
    propagate_endings(entries,15)
    if entries:
        big_time=total_duration(entries)
        print "Date: {}".format(entries[0].date)
        print ""
        print "# Ordered list of topics"
        projects={}
        for entry in entries:
            if entry.title in projects:
               projects[entry.title]+=entry.get_duration()
            else:
               projects[entry.title]=entry.get_duration()
        for key, value in sorted(projects.iteritems(), key=lambda (k,v): (v,k)):
            print "%s: %s" % (value, key)
        print "Total time was {} hours and {} minutes".format(int(total_duration(entries)/60),int(total_duration(entries)%60))
        print "Including"
        catagories=["+Bed","+Family","+Faff","+EQT", "+WWW", "+Overhead", "+Health", "+Exercise", "+Personal"]
        catagory_time=0
        for cat in catagories:
            print "{}".format(format_report(entries,cat))
            catagory_time+=total_duration(entries,cat)
        print "Total time {}".format(minutes_to_string(big_time,"all"))
        print "Catagory time {}".format(minutes_to_string(catagory_time,"catagories"))




def format_report(entires,slug):
    minutes=total_duration(entires,slug)
    return minutes_to_string(minutes,slug)

def minutes_to_string(minutes,slug):
    hours=int(minutes/60)
    minutes_left=int(minutes%60)
    return "{:>2}:{:0>2} for {}".format(hours,minutes_left,slug)



########## Input ##########

def full_detect(config_file='/config.json'):

    print "Watson v2.0"
    print "------------------------------"
    report_on_day(args.filename)

