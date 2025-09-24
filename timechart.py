import datetime
import os




# Running mean/Moving average
def get_running_mean(l, N):
        sum = 0
        result = list(0 for x in l)

        for i in range(0, N):
                sum = sum + l[i]
                result[i] = sum / (i+1)

        for i in range(N, len(l)):
                sum = sum - l[i-N] + l[i]
                result[i] = sum / N

        return result

def create_javascript_file(entries,slug): 
#        entries=[entry for entry in entries if slug in entry.title]
        DAY_COUNT = 26
        total_time = []
        for single_date in (
                datetime.datetime.today() - datetime.timedelta(days=n)
                for n in range(DAY_COUNT)):
                single_date_sessions = [ entry for entry in entries if ( entry.date == single_date.date())]
                element = int( sum( [entry.get_duration() for entry in single_date_sessions]))
                total_time = [element]+total_time
        running_mean = get_running_mean(total_time, 7)
        write_to_javascript(total_time,running_mean,slug[1:])

def write_to_javascript(total_time,running_mean,slug):
        f = open(os.path.dirname(os.path.abspath(__file__))+"/javascript/"+slug+".js", 'w')
        f.write("sessions[\""+slug+"\"]=["+",".join(str(x) for x in total_time)+"];\n")
        f.write("running_mean[\""+slug+"\"]=["+",".join(str(x) for x in running_mean)+"]")
        f.close()
