from icalendar import Calendar, Event
import sys
import datetime
from pytz import UTC  # timezone
import calendar_helper_functions

# Watson is really only designed to parse formats and output them as
# calendar events.  The inputs should know, for example, their start and
# end times already...



def processOyster(content):
        __TIME_FORMAT = "%d-%b-%y %H:%M"
        cal = getCal()
        for x in content:
                if "Start" in x:
                        pass
                else:
                        journey = x.split(',')
                        journeytime = datetime.datetime.strptime(
                                "{} {}".format(journey[0], journey[1]), __TIME_FORMAT)
                        if "Bus Journey" in x:
                                addEvent(
                                    cal,
                                    "Bus Journey",
                                    journeytime,
                                    journeytime +
                                    datetime.timedelta(
                                        minutes=20))
                        else:
                                journeyendtime = datetime.datetime.strptime(
                                        "{} {}".format(journey[0], journey[2]), __TIME_FORMAT)
                                addEvent(
                                    cal, journey[3], journeytime, journeyendtime)
        return cal


def process_hours(content):
        __TIME_FORMAT = "%d/%m/%Y %H:%M"
        cal = getCal()
        for x in content:
                if "Clocked" in x:
                        pass
                else:
                        if "Sleep" in x:
                                journey = x.split(',')
                                print datetime.date.today().strftime(__TIME_FORMAT)
                                print x
                                journeytime = datetime.datetime.strptime(
                                        journey[1].replace('"', ''), __TIME_FORMAT)
                                endtime = datetime.datetime.strptime(
                                        journey[2].replace('"', ''), __TIME_FORMAT)
                                addEvent(
                                    cal, "Sleep", journeytime, endtime)
        return cal



if __name__ == "__main__":
    #write_cal("oyster.ics", processOyster(get_content("inputfiles/oystertest.csv")))
    #write_cal("Sleep.ics", process_hours(get_content("inputfiles/sleep.csv")))

    content = sys.argv[1]
    write_cal("Sleep.ics", process_hours(content))
