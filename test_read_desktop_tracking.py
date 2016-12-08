import pytest
print "Hello"
import read_desktop_tracking



def test_getmatchinglines():
        # MacBook-Air:watson josephreddington$ grep -c gmail testfiles/read_desktop_tracking_test1.txt
        # 14
        lines = read_desktop_tracking.get_matching_lines('testfiles/read_desktop_tracking_test1.txt',['gmail'])
        assert len(lines) == 14

def test_single_session():
        sessions = read_desktop_tracking.get_sessions('testfiles/read_desktop_tracking_test1.txt',['gmail'])
        assert len(sessions) == 1
