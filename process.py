from icalendar import Calendar, Event
import sys
import glob
import datetime
import sys
from pytz import UTC  # timezone
import calendar_helper_functions as icalhelper


# Watson is really only designed to parse formats and output them as
# calendar events.  The inputs should know, for example, their start and
# end times already...



def processOyster(content):
        __TIME_FORMAT = "%d-%b-%y %H:%M"
        cal = icalhelper.get_cal()
        for x in content:
                print x
                if "Date" in x:
                        pass
                elif "Start" in x:
                        pass
                else:
                        journey = x.split(',')
                        journeytime = datetime.datetime.strptime(
                                "{} {}".format(journey[0], journey[1]), __TIME_FORMAT)
                        if "Bus Journey" in x:
                                icalhelper.addEvent(
                                    cal,
                                    "Bus Journey",
                                    journeytime,
                                    journeytime +
                                    datetime.timedelta(
                                        minutes=20))
                        else:
                                journeyendtime = datetime.datetime.strptime(
                                        "{} {}".format(journey[0], journey[2]), __TIME_FORMAT)
                                icalhelper.addEvent(
                                    cal, journey[3], journeytime, journeyendtime)
        return cal


def process_hours(content):
        __TIME_FORMAT = "%d/%m/%Y %H:%M"
        cal = icalhelper.get_cal()
        for x in content:
		print "XX:"+x
                if "Clocked" in x:
                        pass
                else:
                        if "Sleep" in x:
			    if "2016" in x:
                                journey = x.split(',')
                                #print datetime.date.today().strftime(__TIME_FORMAT)
                                #print x
                                journeytime = datetime.datetime.strptime(
                                        journey[1].replace('"', ''), __TIME_FORMAT)
                                endtime = datetime.datetime.strptime(
                                        journey[2].replace('"', ''), __TIME_FORMAT)
                                icalhelper.addEvent(
                                    cal, "Sleep", journeytime, endtime)
				print "event added"+x
	print "returning with calendar"
        return cal



if __name__ == "__main__":
    location="oyster/*.csv"
    content=[]
    for file in glob.glob(location):
        content.extend(icalhelper.get_content(file))
    print content
    processOyster(content)
    #write_cal("Sleep.ics", process_hours(get_content("inputfiles/sleep.csv")))
