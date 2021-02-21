from entry import Entry
import time
import sys
from pathlib import Path

__TIME_FORMAT = "%d/%m/%y %H:%M"

def main(entry): 
    begin=entry.start_epoch()
    end=entry.end_epoch()
    home = str(Path.home())
    start_output=False
    timestamp=""
    command=""
    return_me=[]
    with open(home+'/.bash_history') as f:
        for line in f:
            if '#' in line[:1]:
                #get the number 
                number=int(line[1:]) 
                if number>begin:
                    start_output=True
                if number>end:
                    return return_me
                timestamp=time.strftime(__TIME_FORMAT, time.localtime(number))
            else:
                if len(line)>1:
                    command=line.strip()
                if start_output:
                    string="{}, {}".format(timestamp,command)
                    return_me.append(string)

    return return_me

if __name__ == "__main__":
    commands=main(Entry(sys.argv[1]))
    for command in commands:
        print(command)
