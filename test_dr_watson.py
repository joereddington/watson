from unittest import TestCase
import calendar_helper_functions
import unittest
import watson
import command_list
import json
import os

from entry import Entry
import datetime


def get_content(infilename):
        with open(infilename) as f:
                content = f.readlines()
        return content

class watsonTest(TestCase):

    def test_parse_line_problem(self):
        entry=Entry("## 24/07/19 11:08,  +EQT")
        temp=entry.get_duration()
        self.assertEqual(entry.title,"+EQT")

    def test_parse_line(self):
        entry=Entry("###### 27/08/18 00:01 to 07:53, +Sleep")
        self.assertEqual(entry.title,"+Sleep")

    def test_parse_line_without_date(self):
        entry=Entry("###### 15:17, Making Watson great again.")
        self.assertEqual(entry.title,"Making Watson great again.")

    def test_get_duration(self):
        entry=Entry("###### 15:17 to 15:30, Making Watson great again.")
        self.assertEqual(entry.get_duration(),13)

    def test_get_duration_without_end(self):
        entry=Entry("###### 15:17, Making Watson great again.")
        self.assertEqual(entry.get_duration(),0)

    def test_adding_end_later(self):
        entry=Entry("###### 15:17, Making Watson great again.")
        entry.end="15:33"
        self.assertEqual(entry.get_duration(),16)

    def test_adding_dates(self):
        entries=[]
        content=get_content('testinputs/entrytest.txt')
        for line in content:
            entries.append(Entry(line))
        watson.propagate_dates(entries)
        self.assertEqual(entries[-1].date.day,29)

    def test_adding_end_times(self):
        entries=[]
        content=get_content('testinputs/entrytest.txt')
        for line in content:
            entries.append(Entry(line))
        watson.propagate_endings(entries,15)
        for entry in entries:
            print("{}: {}".format(entry.end,entry.input_string.strip()))
        self.assertEqual(entries[2].end,"08:15")

    def test_parse_line_batch(self):
        content=get_content('testinputs/entrytest.txt')
        for line in content:
            entry=Entry(line)
        self.assertEqual(1,1)

    def test_running_total(self):
        entries=[]
        content=get_content('testinputs/entrytest.txt')
        for line in content:
            entries.append(Entry(line))
        total=watson.total_duration(entries)
        self.assertEqual(total,868)
        total=watson.total_duration(entries,"+Sleep")
        self.assertEqual(total,472)
        total=watson.total_duration(entries,"+Faff")
        self.assertEqual(total,46)

    def test_sleep_total(self):
        entries=[]
        content=get_content('testinputs/entrytest.txt')
        for line in content:
            entries.append(Entry(line))

    def test_day_selection(self):
        entries=[]
        content=get_content('testinputs/test_day_selection.txt')
        for line in content:
            entries.append(Entry(line))
        self.assertEqual(entries[0].is_date("18/12/18"), True)
        self.assertEqual(entries[2].is_date("19/12/18"), True)
        self.assertEqual(entries[2].is_date("29/12/18"), False)

    def test_bug1(self):
        entry=Entry("###### 13:05: ")
        self.assertEqual(entry.title,"")

    def test_get_untagged_entries(self):
        entries=[]
        content=get_content('testinputs/splitontitle.md')
        for line in content:
            try: 
                if line.startswith("##"):
                    entries.append(Entry(line))
            except ValueError:
                    continue
        tagged=watson.get_entries_with_tag(entries,None)
        self.assertEqual(len(tagged),12)

    def test_gitlog(self):
        entries=[]
        content=get_content('testinputs/test_diary.md')
        for line in content:
            try: 
                if "##" in line:
                    entries.append(Entry(line))
            except ValueError:
                    continue
        tagged=watson.get_entries_with_tag(entries,None)
        self.assertEqual(len(tagged),222)

    def test_normalise_for_summer_time(self):
        entry=Entry("## 15/09/19 06:04 ")
        result=calendar_helper_functions.normalise_for_summer_time(entry.start_datetime())
        entry=Entry("## 24/11/19 11:08,  +EQT")
        result=calendar_helper_functions.normalise_for_summer_time(entry.start_datetime())

    def test_bug2(self):
        entries=[]
        content="""## 06/02/21 10:34, How about now?
*some more text"""
        for line in content:
            try: 
                if "##" in line:
                    entries.append(Entry(line))
            except ValueError:
                    continue
        calendar_helper_functions.calendar_output("testoutputs/bug.ics",entries)
        self.assertEqual(2,2)
        
    def test_bug(self):
        entries=[]
        content=get_content('testinputs/bug.md')
        entry=Entry(content[0])
        cal = calendar_helper_functions.get_cal()
        calendar_helper_functions.add_event(cal, entry.title, entry.start_datetime(), entry.end_datetime())
        self.assertEqual(2,2)


    def test_error_when_passing_list(self):
        content=get_content('testinputs/bug.md')#this is a multi line 
        self.assertRaises(ValueError,Entry,content)
        self.assertRaises(ValueError,Entry,"Hello")

    def test_epoch_ouput(self):
        entry=Entry("###### 27/08/18 00:01 to 07:53, +Sleep")
        self.assertEqual(entry.start_epoch(),1535324460)
        self.assertEqual(entry.end_epoch(),1535352780)

    def test_command_history(self):
        entry=Entry("## 19/02/21 11:00 to 12:00, working on this code")
        c_list=command_list.main(entry)
        self.assertEqual(len(c_list),25) 

if __name__=="__main__":
    unittest.main()
