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
    with open(home+'/.bash_history' , 'rt', encoding='latin1') as f: # the encoding fixed a unicdoe error 
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

import locale
if __name__ == "__main__":
    print("The entry was {}".format(sys.argv[1]))
    print(locale.getpreferredencoding(False))
    print()
    print()
    print()
    print()
    commands=main(Entry(sys.argv[1]))
    for command in commands:
        print(command)
    if len(commands)==0:
        print("No Commands found")
