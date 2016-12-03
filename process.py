from icalendar import Calendar, Event
import datetime
from pytz import UTC  # timezone

outfilename = "oysterjourneys.ics"
infilename = "test.csv"


def addEvent(cal, summary, start, end):
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


def write_cal(outfilename, cal):
        f = open(outfilename, 'wb')
        f.write(cal.to_ical())
        f.close()


def processOyster():
        __TIME_FORMAT = "%d-%b-%y %H:%M"
        cal = getCal()
        with open(infilename) as f:
                content = f.readlines()
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
                write_cal(outfilename, cal)


def process_hours(infilename):
        __TIME_FORMAT = "%d/%m/%Y %H:%M"
        cal = getCal()
        outfilename = "sleep.ics"
        with open(infilename) as f:
                content = f.readlines()
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
                write_cal(outfilename, cal)


def process_email(infilename):
        __TIME_FORMAT = "%Y-%m-%d%H:%M:%S"
        cal = getCal()
        with open(infilename) as f:
                content = f.readlines()
                content = [x for x in content if "2016-10" in x]
                breakdown = [(x[:10], x[11:19], x[19:])
                             for x in content if any(a in x[19:] for a in ["Gmail","irmail"])]
                day_bucket = {}
                for thing in breakdown:
                        day_bucket.setdefault(
                            thing[0], []).append(
                            (thing[1], thing[2]))

                outfilename = "emails.ics"
                for key in day_bucket.keys():
                        print "{}  {} {}".format(key, day_bucket[key][0][0],day_bucket[key][-1][0])
                        journeytime = datetime.datetime.strptime( key+day_bucket[key][0][0], __TIME_FORMAT)
                        endtime = datetime.datetime.strptime( key+day_bucket[key][-1][0], __TIME_FORMAT)
                        addEvent(cal, "Processing Email", journeytime, endtime)
                write_cal(outfilename, cal)


processOyster()
#process_email( "/Users/josephreddington/" + "Dropbox/git/DesktopTracking/output/results.txt")

#process_hours("sleep.csv")
