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
#This doesn't deal with the last entry! TODO  
    laststart=entries[-1].start #it must have a value - the last entry is often only half. 
    for entry in reversed(entries):
        if entry.end==entry.start:
            entry.end=laststart
            print(entry)
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





def report_on_day(rawcontent):
    entries=[Entry(line) for line in rawcontent if "## " in line]
    propagate_dates(entries)
    propagate_endings(entries,15)
    if entries:
        print("Total time {}".format(minutes_to_string(total_duration(entries),"all")))
        print("Total time {}".format(minutes_to_string(total_duration(entries,"+EQT"),"EQT")))

def format_report(entires,slug):
    minutes=total_duration(entires,slug)
    return minutes_to_string(minutes,slug)

def minutes_to_string(minutes,slug):
    hours=int(minutes/60)
    minutes_left=int(minutes%60)
    return "{:>2}:{:0>2} for {}".format(hours,minutes_left,slug)


def get_entries_with_tag(entries,matchString):
#Should probably make this a filter to look nice. 
        return_me=[]
        if (matchString==None):
            for entry in entries:
                if ("+" not in entry.title):
                    return_me.append(entry)
        else:
            for entry in entries:
                if  (matchString in entry.title):
                    return_me.append(entry)
        print("Returning with {} entires".format(len(return_me)))
        return return_me


########## Input ##########

def full_detect():

    content=get_content("/Users/joereddingtonfileless/git/inbox.md")
    report_on_day(content)

