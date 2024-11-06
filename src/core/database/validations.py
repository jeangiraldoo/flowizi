import os
import winreg
import re
from tld import get_tld
from urllib.parse import urlparse
from core.database import database


def add_env_validation(env_name):
    '''Calls the function that inserts environments into the database

    Parameters:
    env_name (Str): Name of the environment to add'''
    return database.add_environment(env_name)


def add_website_validation(env_name, url):
    if not verify_URL(url, "website"):
        url = f"https://{url}"
        if not verify_URL(url, "website"):
            return [False, "invalid_url"]

    name = url[url.rfind("/") + 1:]
    result = database.insert_element(env_name, "websites", name, url)

    return [result, "insertion_attempt"]


def add_file_validation(env_name, url):
    if not verify_URL(url, "file"):
        return [False, "file not found"]

    url = url.replace("\\", "/")
    name = url[url.rfind("/") + 1:]

    result = database.insert_element(env_name, "files", name, url)
    return [result, "insertion_attempt"]


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
