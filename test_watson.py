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
        atoms=watson.read_log_file("inputfiles/test.md")
        self.assertEqual(len(atoms),13)

    def test_read_log_file_title1(self):
        atoms=watson.read_log_file("inputfiles/test.md")
        self.assertEqual(atoms[0]['title'],"inputfiles/test.md")

    def test_read_log_file_title2(self):
        atoms=watson.read_log_file("inputfiles/test.md", "hope")
        self.assertEqual(atoms[0]['title'],"hope")

    def test_read_log_file_title2(self):
        atoms=watson.read_log_file("inputfiles/withtitle.md", "hope")
        self.assertEqual(atoms[0]['title'],"safe")

if __name__=="__main__":
    unittest.main()
