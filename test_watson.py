from unittest import TestCase
import unittest
import watson
import urllib
import json
import os
from urllib2 import urlopen, Request


class watsonTest(TestCase):

    def test_download_repo_json(self):
         self.assertEqual(3,3)

    def test_read_log_file(self):
        atoms=watson.read_log_file("testinputs/regressions/livenotes.md")
        self.assertEqual(len(atoms),582)

    def test_read_log_file_inline(self):
        atoms=watson.read_log_file("testinputs/regressions/livenotesinline.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(atoms),582)

    def test_read_log_file_problem(self):
        atoms=watson.read_log_file("testinputs/problem.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),0)

    def test_read_desktop_log_file(self):
        atoms=watson.read_tracking_file("testinputs/desktop.md")
        self.assertEqual(len(atoms),66)

    def test_make_email_sessions(self):
        atoms=watson.read_tracking_file("testinputs/desktop.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),2)




    def test_read_log_file_blanktitle(self):
        atoms=watson.read_log_file("testinputs/regressions/livenotes.md")
        self.assertEqual(atoms[0].title,"testinputs/regressions/livenotes.md")

    def test_read_log_file_proper_title(self):
        atoms=watson.read_log_file("testinputs/regressions/bug-with-markdown-links.md")
        self.assertEqual(atoms[0].title,"Bug with markdown links")

    def test_make_sessions(self):
        atoms=watson.read_log_file("testinputs/regressions/livenotes.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),36)

    def test_read_heartrate_file(self):
        atoms=watson.read_watch_heartrate("testinputs/heart.csv")
        self.assertEqual(len(atoms),164866)

    def test_count_awake_sessions(self):
        TF = "%d-%b-%Y %H:%M"
        pre=watson.max_dist_between_logs
        watson.max_dist_between_logs=90
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        sessions=watson.get_sessions(atoms)
        watson.max_dist_between_logs=pre
        projects = list(set([entry.project for entry in sessions]))
       # for project in projects:
       #         watson.projectreport(project, sessions, True)

        self.assertEqual(len(sessions),140)

    def test_invert_sessions(self):
        pre=watson.max_dist_between_logs
        watson.max_dist_between_logs=90
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        sessions=watson.get_sessions(atoms)
        #print "XXX{}".format(sessions[0])
        sessions=watson.invert_sessions(sessions)
        watson.max_dist_between_logs=pre
        projects = list(set([entry.project for entry in sessions]))
     #   for project in projects:
     #           watson.projectreport(project, sessions, True)
        self.assertEqual(len(sessions),140)


    def test_get_exercise_atoms(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        self.assertEqual(len(atoms),33064)

    def test_get_exercise_sessions(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),58)


    def test_calendar_write(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),58)
        watson.calendar_output('testoutputs/exercise.ics',sessions)
        self.maxDiff = None
        self.assertMultiLineEqual(open('testoutputs/exercise.ics').read().strip(),open('testinputs/exercise.ics').read().strip(),)

    def test_selective_calendar_write(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        sessions=watson.get_sessions(atoms)
        email_atoms=watson.read_tracking_file("testinputs/desktop.md")
        email_sessions=watson.get_sessions(email_atoms)
        sessions.extend(email_sessions)
        watson.calendar_output('testoutputs/exerciseSelective.ics',sessions, 'Exercise')
        self.maxDiff = None
        self.assertMultiLineEqual(open('testoutputs/exerciseSelective.ics').read().strip(),open('testinputs/exercise.ics').read().strip(),)

    def test_fullregression(self):
        watson.args =lambda:None
        setattr(watson.args, 'action', 'sort')
        setattr(watson.args, 'd',None)
        setattr(watson.args, 'verbatim',None)
        self.assertEqual(watson.full_detect(),datetime.timedelta(85, 47940))

    def test_time_split(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.read_watch_heartrate("testinputs/heartshort.csv")
        start="02-Jan-2017 12:27"
        end="02-Jan-2017 16:27"
        atoms=watson.cut(atoms,start,end)
        self.assertEqual(len(atoms),1036)




if __name__=="__main__":
    unittest.main()
