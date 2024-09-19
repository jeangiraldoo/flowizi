import pytest
from app_core import meetings

@pytest.mark.parametrize("time, expected", [
    ("20:40", True),
    ("30:50", False),
    ("kfskfsk", False),
    ("20:d2", False),
    ("af:fs", False),
    ("2345:23", False),
    ("20:60", False),
    ("01:60", False)
])
def test_validate_time(time, expected):
    test_meeting = meetings.meeting("test_meeting", "test_link")
    assert meetings.meeting.validate_time(test_meeting, time) == expected 

