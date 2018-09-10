from unittest import TestCase
import unittest
import watson
import urllib
import json
import os

import atom
import session
from entry import Entry
import datetime
from urllib2 import urlopen, Request


def get_content(infilename):
        with open(infilename) as f:
                content = f.readlines()
        return content




class watsonTest(TestCase):


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
            print "{}: {}".format(entry.end,entry.input_string.strip())
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


    def test_bug1(self):
        entry=Entry("###### 13:05: ")
        self.assertEqual(entry.title,None)

    def test_bug2(self):
        content=get_content('testinputs/bug2.txt')
	entries=[]
        for line in content:
	 if "###" in line:
            entries.append(Entry(line))
	for entry in entries:

	    print "X{}".format(entry)
        total=watson.total_duration(entries,"+Sleep")
        self.assertEqual(total,472)
        total=watson.total_duration(entries,"+Faff")
        self.assertEqual(total,46)



if __name__=="__main__":
    unittest.main()
