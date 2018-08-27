import re
import datetime

class Entry(object):


        def __init__(self, input_string):
            self.input_string=input_string
            match = re.search(r'\d{2}/\d{2}/\d{2}', input_string)
            if match:
                self.date = datetime.datetime.strptime(match.group(), '%y/%m/%d').date()
            else:
                self.date = None
            match = re.search(r',\s(?P<title>.*)', input_string)
            self.title =match.group("title").strip()

        def get_title(self):
            return self.title
