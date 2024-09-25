import pytest
from src.app_core import flowizi

test_object = flowizi.Flowizi()
@pytest.mark.parametrize("url, expected", [
    ("https://google.com", True),
    ("https:kjfakfkj", False),
    ("hola", False),
    ("", False),
    ("hola.com", False)
])
def test_verify_URL(url, expected):
    assert test_object.verify_URL(url) == expected 
