import os
import re
from tld import get_tld
from urllib.parse import urlparse


def verify_URL(url: str, element_type: str) -> bool:
    "Checks if a URL is valid"
    if element_type == "website":
        return verify_website_url(url)
    elif element_type == "file":
        return verify_file_url(url)


def verify_website_url(url) -> bool:
    parsed_url = urlparse(url)
    scheme = parsed_url.scheme
    netloc = parsed_url.netloc
    if not scheme and not netloc:
        return False

    if not has_valid_tld(url):
        return False

    if not re.match("[a-z]", netloc[0]):
        return False

    if not re.match("[a-z]", netloc[len(netloc) - 1]):
        return False

    if "." not in netloc:
        return False

    if ".." in netloc:
        return False

    return True


def has_valid_tld(url: str) -> bool:
    # If the URL doesn't have a scheme (protocol), add "http://"
    try:
        get_tld(url, fail_silently=False)  # Attempt to parse the TLD
        return True
    except ValueError:
        return False


def verify_file_url(url) -> bool:
    if not os.path.exists(url):
        return False
    return True
