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
import calendar_helper_functions
from entry import Entry


# Todo: 
# 1. Should be more resilient to false positives - currently this file has a 'If startswith' to decide if it's an entry and entry must parse, should be that entry checks to see if it's reasonable text, or asks nicely if the entry is well formed.

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
            print "here" 
            print entry
            if entry.get_duration()>max_minutes:
                entry.end=entry.start
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
    parser.add_argument('-d', nargs="?" , help="Show only entries that are at least this many days old")
    parser.add_argument('-t', action='store_true', help="Show only today")
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



def report_on_day(rawcontent):
    entries=[]
    for line in rawcontent:
	try: 
	    if line.startswith("##"):
		entries.append(Entry(line))
	except ValueError:
		continue
    propagate_dates(entries)
    propagate_endings(entries,15)
    if args.t: #if it must be today...
	entries=[entry for entry in entries if entry.is_today()]
    if args.d: 
	entries=[entry for entry in entries if entry.days_old()<int(args.d)] 
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
        catagories=["+Bed","+PlanningAndTracking","+Family", "+Email", "+Faff","+EQT", "+WWW", "+Overhead", "+Health", "+Exercise", "+PersonalProject"]
        catagory_time=0
        for cat in catagories:
	    timechart.create_javascript_file(entries,cat)
            calendar_helper_functions.calendar_output(cat+".ics",entries,cat)
            print "{}".format(format_report(entries,cat))
            catagory_time+=total_duration(entries,cat)
        calendar_helper_functions.calendar_output("untagged.ics",get_entries_with_tag(entries,None),None)
        print "Total time {}".format(minutes_to_string(big_time,"all"))
        print "Category time {}".format(minutes_to_string(catagory_time,"Categories"))




def format_report(entires,slug):
    minutes=total_duration(entires,slug)
    return minutes_to_string(minutes,slug)

def minutes_to_string(minutes,slug):
    hours=int(minutes/60)
    minutes_left=int(minutes%60)
    return "{:>2}:{:0>2} for {}".format(hours,minutes_left,slug)


def get_entries_with_tag(entries,matchString):
        return_me=[]
        if (matchString==None):
            for entry in entries:
                if ("+" not in entry.title):
                    return_me.append(entry)
        else:
            for entry in entries:
                if  (matchString in entry.title):
                    return_me.append(entry)
        print "Returning with {} entires".format(len(return_me))
        return return_me


########## Input ##########

def full_detect():

    print "Watson v2.0"
    print "------------------------------"
    content=get_content(args.filename)
    report_on_day(content)

