import datetime

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

def graph_out(sessions,slug):
        DAY_COUNT = 26
        total_time = []
        for single_date in (
                datetime.datetime.today() - datetime.timedelta(days=n)
                for n in range(DAY_COUNT)):
                single_date_sessions = [
                    entry for entry in sessions if (
                        entry.start.date() == single_date.date())]
                element = int(
                              sum(
                                  [entry.length()
                                   for entry in single_date_sessions],
                                  datetime.timedelta()).total_seconds() / 60)
                total_time = [element]+total_time
        running_mean = get_running_mean(total_time, 7)
        write_to_javascript(total_time,running_mean,slug)

def write_to_javascript(total_time,running_mean,slug):
        f = open("javascript/"+slug+".js", 'wb')
        f.write(slug+"sessions=["+",".join(str(x) for x in total_time)+"];\n")
        f.write(slug+"running_mean=["+",".join(str(x) for x in running_mean)+"]")
        f.close()
