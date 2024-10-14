import pytest
from src.elements.element_utils import utils

@pytest.mark.parametrize("url, expected", [
    ("https://google.com", True),
    ("https://google.com.co", True),
    ("https://jean.io", True),
    ("", False),
    ("hola", False),
    ("hola.com", False),
    ("https:kjfakfkj", False),
    ("https://lol", False),
    ("jean.io", False),
    ("https://jean.ia", False),
    ("https://.google.com", False),
    ("https://google.com.", False),
    ("https://google..com", False),
    ("https://google....com", False)
])
def test_verify_URL(url, expected):
    assert utils.verify_URL(url, "website") == expected 
