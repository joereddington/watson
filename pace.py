import re
import calendar_helper_functions as icalhelper
import datetime

__TIME_FORMAT = "%d/%m/%y %H:%M"

max_dist_between_logs = 15  # in minutes TODO these should be arguments for different types of input.
min_session_size = 15  # in minutes


class Session(object):
        project = "Unknown"
        start = ""
        end = ""
        content = ""

        def __init__(self, project, start, end, content):
                print "hello"
                self.project, self.start, self.end = project, start, end

        def length(self):
                return self.end-self.start

        def __str__(self):
                return "    {} to {} ({})".format(
                    self.start, self.end.time(), self.length())



def get_e(atom):
        total_date=atom['date']+" "+atom['end']
        return datetime.datetime.strptime(total_date,__TIME_FORMAT)


def get_s(atom):
        total_date=atom['date']+" "+atom['start']
        return datetime.datetime.strptime(total_date,__TIME_FORMAT)

def get_sessions(atoms):

        #Make this three functions - one grouping, one removing small ones, and the other converting the list to a session.
        last= datetime.datetime.strptime(
            "11/07/10 10:00", __TIME_FORMAT)
        current = get_e(atoms[0])
        grouped_timevalues=[]
        current_group=[]
        for current in atoms:
                if ((get_s(current)-last) > datetime.timedelta(
                        minutes=max_dist_between_logs)):
                        grouped_timevalues.append(current_group)
                        current_group=[current]
                else:
                        last = get_e(current)
                current_group.append(current)
        grouped_timevalues.append(current_group)
        sessions = []
        for i in grouped_timevalues:
            if i:
                print "there"
                if ((get_s(i[-1])-get_e(i[0]))> datetime.timedelta(minutes=min_session_size)):
                    print "Hello"
                    sessions.append(Session(title,get_s(i[0]),get_e(i[-1]),i))
        print sessions
        return sessions


filename="/Users/josephreddington/pacesetter.md"
content="\n".join(icalhelper.get_content(filename))
entries=content.split("######")
atoms=[]
atom={}
lastdate="01/01/10"
date=""
for e in entries:
    if len(e)<10:
        continue
    lines=e.split("\n")
    atom['content']="\n".join(lines[1:]).strip()+"\n"
    atom['start']=""
    date= e.split("\n")[0]
    date=date.replace("2016-","16 ")
    date=date.replace("2017-","17 ")
    date=re.sub(r":[0-9][0-9] GMT","",date)
    date=re.sub(r":[0-9][0-9] BST","",date)
    date=re.sub(r"to [0-9][0-9]/../..","to",date)
    if date.find("/")>0: #Then we have both date and time.
        newdate=date[:9].strip()
        atom['start']=date[9:len(date)].strip()
        atom['date']=newdate
        lastdate=newdate
    else:
        atom['start']=date.strip()[:5]
        atom['date']=lastdate
    if len(atom['start'])>6:
        #Then it was a 'to' construct and has a start and end time
        atom['end'] = atom['start'][9:]
        atom['start'] = atom['start'][:5]
    else:
        atom['end']=atom['start']
    atom['start']=atom['start'][:5]
    atom['end']=atom['end'][:5]
    atoms.append(atom.copy())

previous_date=""

get_sessions(atoms)
#for atom in atoms:
#  if atom['date']==previous_date:
#    print "###### "+atom['start']+ "Where is the end time???"
#  else:
#    print "###### "+atom['date']+ " "+ atom['start']+ "Where is the end time???"
#    previous_date=atom['date']
#  print atom['content']
#  print "____________________________________________________________________________"



