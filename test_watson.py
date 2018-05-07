from unittest import TestCase
import unittest
import watson
import urllib
import json
import os
import atom
import session
import datetime
from urllib2 import urlopen, Request


class watsonTest(TestCase):




    def test_fast_strptime(self):
        test1="02/07/17 15:22"
        TIME_FORMAT = "%d/%m/%y %H:%M"
        result=atom.fastStrptime(test1,TIME_FORMAT)
        otherresult=datetime.datetime.strptime(test1,TIME_FORMAT)

        self.assertEqual(result,otherresult)


    def test_fast_strptime_from_watch(self):
        test1="01-Jan-2018 07:22"
        TIME_FORMAT = "%d-%b-%Y %H:%M"
        result=atom.fastStrptime(test1,TIME_FORMAT)
        otherresult=datetime.datetime.strptime(test1,TIME_FORMAT)

        self.assertEqual(result,otherresult)



    def test_download_repo_json(self):
         self.assertEqual(3,3)

    def test_log_file_to_atoms(self):
        atoms=watson.log_file_to_atoms("testinputs/regressions/livenotes.md")
        self.assertEqual(len(atoms),582)

    def test_log_file_to_atoms_inline(self):
        atoms=watson.log_file_to_atoms("testinputs/regressions/livenotesinline.md")
        self.assertEqual(len(atoms),582)

    def test_commandline_file_to_atoms(self):
        atoms=watson.commandline_file_to_atoms("testinputs/commandline.txt")
        self.assertEqual(len(atoms),6475)

    def test_log_file_to_atoms_problem(self):
        atoms=watson.log_file_to_atoms("testinputs/problem.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),0)

    def test_read_desktop_log_file(self):
        atoms=watson.desktop_tracking_file_to_atoms("testinputs/desktop.md")
        self.assertEqual(len(atoms),66)

    def test_make_email_sessions(self):
        atoms=watson.desktop_tracking_file_to_atoms("testinputs/desktop.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),2)

    def test_get_sessions_works_with_no_atoms(self):
        atoms=[]
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),0)



    def test_log_file_to_atoms_blanktitle(self):
        atoms=watson.log_file_to_atoms("testinputs/regressions/livenotes.md")
        self.assertEqual(atoms[0].title,"testinputs/regressions/livenotes.md")

    def test_log_file_to_atoms_proper_title(self):
        atoms=watson.log_file_to_atoms("testinputs/regressions/bug-with-markdown-links.md")
        self.assertEqual(atoms[0].title,"Bug with markdown links")

    def test_make_sessions(self):
        atoms=watson.log_file_to_atoms("testinputs/regressions/livenotes.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),36)

    def test_read_heartrate_file(self):
        atoms=watson.heartrate_to_atoms("testinputs/heart.csv")
        self.assertEqual(len(atoms),164866)

    def test_count_awake_sessions(self):
        watson.args =lambda:None
        setattr(watson.args, 'action', 'sort')
        setattr(watson.args, 'd',None)
        setattr(watson.args, 'verbatim',None)
        TF = "%d-%b-%Y %H:%M"
        pre=watson.max_dist_between_logs
        watson.max_dist_between_logs=90
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        sessions=watson.get_sessions(atoms)
        watson.max_dist_between_logs=pre
        projects = list(set([entry.project for entry in sessions]))
       # for project in projects:
       #         watson.projectreport(project, sessions, True)

        self.assertEqual(len(sessions),140)

    def test_invert_sessions(self):
        pre=watson.max_dist_between_logs
        watson.max_dist_between_logs=90
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
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
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        self.assertEqual(len(atoms),33064)


    def test_get_image_atoms(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.camera_uploads_to_atoms("testinputs/images/")
        self.assertEqual(len(atoms),5)

    def test_output_image_atoms(self):
        #Sorting is based on last modified time, which on macs is done to the minute, event if the filename is done to the second, hence this can look like it' in the wrong order.
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.camera_uploads_to_atoms("testinputs/images/")
        image_text=watson.atoms_to_text(atoms)
        image_text=image_text.replace("\n\n","\n")
        self.maxDiff = None
        print image_text
        self.assertMultiLineEqual(open('testoutputs/image.md').read().strip(),image_text.strip())

        self.assertEqual(len(atoms),5)


    def test_combination(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.camera_uploads_to_atoms("testinputs/images/")
        atoms.extend(watson.log_file_to_atoms("testinputs/augment1.md"))
        sorted_atoms=sorted(atoms,key=lambda x: x.get_S(), reverse=False)

        image_text=watson.atoms_to_text(sorted_atoms)
        image_text=image_text.replace("\n\n","\n")
        self.maxDiff = None
        print image_text
        self.assertMultiLineEqual(open('testoutputs/augment1result.md').read().strip(),image_text.strip())




    def test_get_exercise_sessions(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),58)


    def test_calendar_write(self):
        watson.args =lambda:None
        setattr(watson.args, 'action', 'sort')
        setattr(watson.args, 'd',None)
        setattr(watson.args, 'verbatim',None)

        TF = "%d-%b-%Y %H:%M"
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),58)
        watson.calendar_output('testoutputs/exercise.ics',sessions)
        self.maxDiff = None
        self.assertMultiLineEqual(open('testoutputs/exercise.ics').read().strip(),open('testinputs/exercise.ics').read().strip(),)

    def test_selective_calendar_write(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        atoms=watson.get_atom_clusters(atoms)
        sessions=watson.get_sessions(atoms)
        email_atoms=watson.desktop_tracking_file_to_atoms("testinputs/desktop.md")
        email_sessions=watson.get_sessions(email_atoms)
        sessions.extend(email_sessions)
        watson.calendar_output('testoutputs/exerciseSelective.ics',sessions, 'Exercise')
        self.maxDiff = None
        self.assertMultiLineEqual(open('testoutputs/exerciseSelective.ics').read().strip(),open('testinputs/exercise.ics').read().strip(),)



    def test_fullregression2018_01_01(self):
        watson.args =lambda:None
        setattr(watson.args, 'action', 'sort')
        setattr(watson.args, 'd',None)
        setattr(watson.args, 'verbatim',None)
        self.assertEqual(watson.full_detect('/testinputs/full2018-01-01/config.json'),datetime.timedelta(53, 18600))



    def test_time_split(self):
        TF = "%d-%b-%Y %H:%M"
        atoms=watson.heartrate_to_atoms("testinputs/heartshort.csv")
        start="02-Jan-2017 12:27"
        end="02-Jan-2017 16:27"
        atoms=watson.cut(atoms,start,end)
        self.assertEqual(len(atoms),1036)

    def test_journal_bug(self):
        atoms=watson.log_file_to_atoms("testinputs/strange.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),1)


    def test_midnight_bug(self):
        atoms=watson.log_file_to_atoms("testinputs/midnight.md")
        sessions=watson.get_sessions(atoms)
        self.assertEqual(len(sessions),1)

    def test_print_original_identity(self):
        atoms=watson.log_file_to_atoms("testinputs/strange.md")
        strange_text=watson.atoms_to_text(atoms)
        strange_text=strange_text.replace("\n\n","\n")
        self.maxDiff = None
        print strange_text
        self.assertMultiLineEqual(open('testinputs/strange.md').read().strip(),strange_text)


if __name__=="__main__":
    unittest.main()
