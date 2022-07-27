#!/usr/bin/python
from entry import Entry

def get_content(infilename):
        with open(infilename) as f:
                content = f.readlines()
        return content

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
            if entry.get_duration()>max_minutes:
                entry.end=entry.start
        laststart=entry.start

def total_duration(entries,matchtext=""):
    running_total=0
    for entry in entries:
        if matchtext in entry.title:
            running_total+=entry.get_duration()
    return running_total


def report_on_day(rawcontent):
    # Here's what what I want. 
    # Total time on calendar 
    # EQT time on calendar 
    # Time left to reach eight hours 
    # Time left before 5pm. 
    entries=[Entry(line) for line in rawcontent if "## " in line]
    propagate_dates(entries)
    propagate_endings(entries,15)
    # Total time on calendar 
    print("Total time      {}".format(minutes_to_string(total_duration(entries))))
    # EQT time on calendar 
    print("EQT time        {}".format(minutes_to_string(total_duration(entries,"+EQT"))))
    # Time left to work 
    print("Left to do      {}".format(minutes_to_string(60*8-total_duration(entries,"+EQT"))))
    # Time left before 5pm. 
    import datetime 
    now = datetime.datetime.now()
    fivepm = datetime.time(hour=17,minute=0)
    fivepm =datetime.datetime.combine(now,fivepm)
    timeleft=fivepm-now 
    minutesleft=timeleft.seconds/60 
    print("Time until 5pm  {}".format(minutes_to_string(minutesleft)))
    



def minutes_to_string(minutes):
    hours=int(minutes/60)
    minutes_left=int(minutes%60)
    return "{:>2}:{:0>2}".format(hours,minutes_left)


def full_detect():
    content=get_content("/Users/joe2021/git/inbox.md")
    report_on_day(content)

full_detect()
