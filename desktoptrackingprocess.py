#!/usr/bin/python
"Module for compiling tracking data in bar chart"
from __future__ import division
import datetime
import time
from icalendar import Calendar, Event

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, date, timedelta

# First! I want Columns to identify a period of an hour of NO readings and
# overlay it as black! Then I want to use that as a split....

# So we're going to add some aspects to this - chief amoung them the ability to split days into several parts.
# The first stage is to be able to do it for an individual day - and the
# easy way of doing that is to give each day a start and end time and then
# put another graph ontop - see how that looks. Ideally, of course, I'd also
# like this to export to my calendar.

__DAY_COUNT = 7
__HOME_DIR = "/Users/josephreddington/Dropbox/Dreamhost/joereddington.com/stress/"
__OUTPUT_FILE = __HOME_DIR + 'columns.png'
weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] * __DAY_COUNT * 2




def addEvent(cal, summary, start,end):
    event = Event()
    event.add('summary', summary)
    event.add('dtstart', start)
    event.add('dtend', end)
    event.add('dtstamp', end)
    event['uid'] = summary+str(start)+str(end)
    event.add('priority', 5)

    cal.add_component(event)


def getCal():
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    return cal

def write_cal(outfilename,cal):
        f = open(outfilename, 'wb')
        f.write(cal.to_ical())
        f.close()



class FullRotation(object):
        WINDOW_TITLE_FILE = "/Users/josephreddington/" + "Dropbox/git/DesktopTracking/output/results.txt"
        __WAKE_FILE = "/Users/josephreddington/" + "Dropbox/git/Columns/chestopenings.txt"
        dayactivities = []
        date = ""

        def __init__(self, single_date):
                self.date = single_date
                self.dayactivities = self.get_activity_list_for_date(
                        self.WINDOW_TITLE_FILE, single_date)

        def __str__(self):
                return weekdays[self.date.weekday(
                        )] + " " + str(self.date) + "\n" + '\n'.join(str(item) for item in self.dayactivities)

        def get_activity_list_for_date(self, filename, single_date):
                "returns a filled in activity list for the given date"
                datestring = time.strftime("%Y-%m-%d", single_date.timetuple())
                item_list = self.construct_activity_list(datestring)
                self.process_logfile(filename, datestring, item_list)
                normalise_activity_list(item_list)
                return item_list

        def process_logfile(self, filename, datestring, item_list):
                "compares every line in a file with the triggers in a list of activity recorders"
                log_file = open(filename)
                line = log_file.readline()
                while line:
                        if datestring in line:
                                seconds_since_midnight = (datetime.strptime(
                                        line[11:19], '%H:%M:%S') - get_first()).total_seconds()
                                if seconds_since_midnight > 13000:
                                        for item in item_list:
                                                item.examine(line)
                        line = log_file.readline()
                return item_list

        def construct_activity_list(self, datestring):
                "constructs the activity list and also processes the wake file"
                item_list = []
                item_list.append(
                    ActivityRecorder(
                        "email", ["firefox:Inbox", "Gmail", "Airmail"],
                        "red"))
                return item_list


class ActivityRecorder(object):

        "For each activity tracked we record the set of triggers and the relevant meta data"
        search_strings = []
        seconds_first, seconds_last = 0, 0
        name, color, first_seen, last_seen = "", "", "", ""

        def __init__(self, name, search_string, color):
                self.name, self.search_strings, self.color = name, search_string, color

        def __str__(self):
                return self.name.ljust(10) + "%s (%d) until %s (%d)" % (
                        self.first_seen, self.seconds_first, self.last_seen, self.seconds_last)

        def examine(self, line):
                "checks an individual line for triggers"
                if any(s in line for s in self.search_strings):
                        if self.first_seen is "":
                                self.first_seen = line[11:19]
                        self.last_seen = line[11:19]


def get_first():
        "helper function for readability"
        return datetime.strptime('00:00:00', '%H:%M:%S')


def convert(in_time):
        "helper function converting '%H:%M:%S' to seconds"
        if in_time is "":
                return 0
        return (datetime.strptime(in_time, '%H:%M:%S') -
                get_first()).total_seconds()


def normalise_activity_list(item_list):
        "converts the activity so that the seconds of first and last usage are availible"
        for item in item_list:
                item.seconds_first = convert(item.first_seen)
                item.seconds_last = convert(item.last_seen)


def mark_section(ind, main_list, index):
        "places the indexed item of the main_list onto the chart using the activity color"
        top = [main_list[i][index].seconds_last - main_list[i]
               [index].seconds_first for i in range(__DAY_COUNT)]
        start = [main_list[i][index].seconds_first for i in range(__DAY_COUNT)]
        plt.bar(ind, top, 0.35, color=main_list[0][index].color, bottom=start)


def get_average_sleep_time(main_list):
        "outputs information on the average sleep/wake time, days without a sleep time aren't counted"
        wake_times = filter(None,
                            [main_list[i][0].seconds_first
                             for i in range(__DAY_COUNT)])
        try:
                average_seconds = sum(wake_times) / len(wake_times)
                m, s = divmod(average_seconds, 60)
                h, m = divmod(m, 60)
        except ZeroDivisionError:  # because the chest file might be blank for a start
                h, m, s = (0, 0, 0)
        return "Average boot time: %d:%02d:%02d" % (h, m, s)
        # credit to http://stackoverflow.com/a/775075


def run():
        cal=getCal()
        "the main run function, heart of the program"
        activity_recorder_list = []
        for single_date in (date.today() - timedelta(days=n)
                            for n in range(__DAY_COUNT)):
                day = FullRotation(single_date)
                print day.date
                print day.dayactivities[0].name
                if day.dayactivities[0].first_seen is "":
                    print "Not today!"
                else:
                    startdate=datetime.strptime("{} {}".format(str(day.date), day.dayactivities.first_seen), '%H:%M:%S')
                    addEvent(cal, "Processing Emails", startdate,enddate)
                    print "here!"
                activity_recorder_list.insert(0, day.dayactivities)

        plt.savefig(__OUTPUT_FILE, dpi=200)

if __name__ == "__main__":
        run()
