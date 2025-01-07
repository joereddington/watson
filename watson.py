#!/usr/bin/python

import datetime
import json
from collections import defaultdict
import re
from entry import Entry

# Constants
HOURS_IN_DAY = 8
END_HOUR = 16
END_MINUTE = 10
MAX_DURATION = 15

def get_content(infilename):
    """Read the content of a file and return it."""
    with open(infilename) as f:
        return f.readlines()

def propagate_dates(entries):
    """Ensure each entry has an associated date."""
    current_date = None
    for entry in entries:
        if entry.date:
            current_date = entry.date
        entry.date = current_date

def propagate_endings(entries, max_minutes):
    """Propagate end times for entries."""
    laststart = entries[-1].start
    for entry in reversed(entries):
        if entry.end == entry.start:
            entry.end = laststart
            if entry.get_duration() > max_minutes:
                entry.end = entry.start
        laststart = entry.start

def total_duration(entries, matchtext=""):
    """Compute total duration for entries matching a given text."""
    return sum(entry.get_duration() for entry in entries if matchtext in entry.title)

def minutes_to_string(minutes):
    """Convert minutes to a formatted string."""
    hours, minutes_left = divmod(minutes, 60)
    return "{:>2}:{:0>2}".format(int(hours), int(minutes_left))

def string_to_entries(rawcontent):
    """Generate and print the day's report."""
    pattern = r'^## \d{2}/\d{2}/\d{2} \d{2}:\d{2}'
    entries = [Entry(line) for line in rawcontent if re.match(pattern, line)]

    propagate_dates(entries)
    propagate_endings(entries, MAX_DURATION)
    return entries

def print_line(start,entries,tag=""):
    entries=[entry for entry in entries if tag in entry.title]
    print("{}{}".format(start,minutes_to_string(total_duration(entries))))


def print_report_on_entries(entries):
    print_line ("Total time        ",entries)
    print_line ("EQT time          ",entries,"+EQT")
    print_line ("RHUL time         ",entries,"+RHUL")
    print_line ("TODO time         ",entries,"+TODO")
    print_line ("BOOK time         ",entries,"+BOOK")
    print_line ("With URL          ",entries,"http")
    print("+EQT Left to do       {}".format(minutes_to_string(60 * HOURS_IN_DAY - total_duration(entries, "+EQT"))))
   
    now = datetime.datetime.now()
    endtime = datetime.datetime.combine(now, datetime.time(hour=END_HOUR, minute=END_MINUTE))
    minutesleft = (endtime - now).seconds / 60
    print("Time until {}.{} {}".format(END_HOUR, END_MINUTE, minutes_to_string(minutesleft)))

def full_detect(filename):
    """Main function to generate the report from a given file."""
    content = get_content(filename)
    entries=string_to_entries(content)
    print_report_on_entries(entries) 


def report(entries,daysold=1):
    entries=[X for X in entries if X.days_old()<daysold]
    print_report_on_entries(entries)


def export_to_json(entries,daysold=1):
    entries=[X for X in entries if X.days_old()<daysold]
    daily_data = defaultdict(lambda: defaultdict(float))  # Nested dictionary

    for entry in entries:
        if entry.date:
            day_str = entry.date.strftime("%Y-%m-%d")
            daily_data[day_str][entry.title] += entry.get_duration() / 60  # Convert to hours

    # Find the full date range
    all_dates = sorted(daily_data.keys())
    start_date = datetime.datetime.strptime(all_dates[0], "%Y-%m-%d")
    end_date = datetime.datetime.strptime(all_dates[-1], "%Y-%m-%d")
    date_range = [(start_date + datetime.timedelta(days=i)).strftime("%Y-%m-%d") 
                  for i in range((end_date - start_date).days + 1)]

    # Fill in missing dates with empty periods
    data = []
    for date in date_range:
        periods = [{"label": label, "hours": hours} for label, hours in daily_data[date].items()] if date in daily_data else []
        data.append({"date": date, "periods": periods})

    # Pretty-print JSON with indentation
    with open("report.json", "w") as f:
        json.dump(data, f, indent=4)

if __name__ == "__main__":
    content = get_content("/home/joe/git/diary/inbox.md")
    entries=string_to_entries(content)
    content = get_content("/home/joe/git/diary/index.md")
    entries.extend(string_to_entries(content))
    export_to_json(entries,7)
    print("Today")
    report(entries)
    print("Last seven days")
    report(entries,7)
