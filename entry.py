import re
import datetime

class Entry(object):


        def __init__(self, input_string):
          try:
            self.input_string=input_string
            match = re.search(r'\d{2}/\d{2}/\d{2}', input_string)
            if match:
                self.date = datetime.datetime.strptime(match.group(), '%y/%m/%d').date()
            else:
                self.date = None
            self.start=None
            self.end=None
            match = re.search(r'(?P<start>\d{2}:\d{2}) to (?P<end>\d{2}:\d{2})', input_string)
            if match:
                self.start = match.group('start')
                self.end = match.group('end')
            match = re.search(r',\s*(?P<title>.*)', input_string)
            self.title =match.group("title").strip()


          except AttributeError as err:
            print "Exception! On this line:"
            print input_string
            raise err


        def get_title(self):
            return self.title

        def get_duration(self):
            #from https://stackoverflow.com/a/3096984/170243
            from datetime import datetime
            FMT = '%H:%M'
            tdelta = datetime.strptime(self.end, FMT) - datetime.strptime(self.start, FMT)
            return tdelta.total_seconds()/60 #returns in minutes
