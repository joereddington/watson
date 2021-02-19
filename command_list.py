from entry import Entry
import time
from pathlib import Path

__TIME_FORMAT = "%d/%m/%y %H:%M"

def main(entry): 
    begin=entry.start_epoch()
    end=entry.end_epoch()
    home = str(Path.home())
    start_printing=False
    timestamp=""
    command=""
    return_me=[]
    with open(home+'/.bash_history') as f:
        for line in f:
            if '#' in line[:1]:
                #get the number 
                number=int(line[1:]) 
                if number>begin:
                    start_printing=True
                if number>end:
                    return return_me
                timestamp=time.strftime(__TIME_FORMAT, time.localtime(number))
            else:
                if len(line)>1:
                    command=line.strip()
                if start_printing:
                    string="{}, {}".format(timestamp,command)
                    print(string)
                    return_me.append(string)

    return return_me
