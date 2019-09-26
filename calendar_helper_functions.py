from icalendar import Calendar, Event
import pytz
import datetime

def normalise_for_summer_time(dt):
        bst = pytz.timezone('Europe/London')
        return  bst.localize(dt).astimezone(pytz.utc)



def calendar_output(filename,entries, matchString=None):
        cal = get_cal()
        for entry in entries:
            if (matchString==None) or (matchString in entry.title):
                add_event(cal, entry.title, normalise_for_summer_time(entry.start_datetime()), normalise_for_summer_time(entry.end_datetime()))
        write_cal(filename,cal)


def add_event(cal, summary, start, end):
        event = Event()
        event.add('summary', summary)
        event.add('dtstart', start)
        event.add('dtend', end)
        event.add('dtstamp', end)
        event['uid'] = summary+str(start)+str(end)
        event.add('priority', 5)

        cal.add_component(event)


def get_cal():
        cal = Calendar()
        cal.add('prodid', '-//My calendar product//mxm.dk//')
        cal.add('version', '2.0')
        return cal


def write_cal(outfilename, cal):
        f = open(outfilename, 'wb')
        f.write(cal.to_ical())
        f.close()



def get_content(infilename):
        with open(infilename) as f:
                content = f.readlines()
        return content

