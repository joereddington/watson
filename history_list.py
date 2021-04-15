from entry import Entry
import sqlite3
import time
import sys
from pathlib import Path

__TIME_FORMAT = "%d/%m/%y %H:%M"
summer="3600"  #This is the summer time hack
#summer="0"  

def get_history_from_database(filename, start, end):
    cursor = sqlite3.connect(filename).cursor()
    cursor.execute('''SELECT datetime((moz_historyvisits.visit_date/1000000)+'''+summer+''','unixepoch'), moz_places.url, title , visit_date FROM moz_places, moz_historyvisits WHERE moz_places.id = moz_historyvisits.place_id and visit_date>{} and visit_date<{}'''.format(start,end))
    return cursor.fetchall()


def main(entry): 
    begin=entry.start_epoch()*1000000
    end=entry.end_epoch()*1000000
    return_me=[]
    data=get_history_from_database('databases/firefox.sqlite',begin,end) 
    for line in data:
            timestamp=line[0]
            location=line[1]
            string="{}, {}".format(timestamp,location)
            return_me.append(string)
    return return_me

if __name__ == "__main__":
    history=main(Entry(sys.argv[1]))
    for command in history:
        print(command)
