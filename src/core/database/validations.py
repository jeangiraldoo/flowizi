import os
import re
from tld import get_tld
from urllib.parse import urlparse
from core.database import database


def add_env_validation(env_name: str) -> bool:
    """Validates if an environment can be inserted into the database.

    Args:
        env_name (Str): Name of the environment to add.
    Returns:
        bool: True if the environment was successfully added.
              False if there's already an environment with the same name.
    """
    env_id = database.get_element_ID("environments", env_name)
    if env_id:
        return False

    database.add_environment(env_name)
    return True


def add_elem_validation(env_name: str, elem_type: str, url: str) -> list[bool, str]:
    """Validates if an element can be inserted into the database based or not.

    Args:
        env_name (str): Name of the environment to add the element to.
        elem_type (str): Type of element (e.g., "websites" or "files").
        url (str): URL or path of the element.

    Returns:
        list[bool, ValidationResult]: A list where the first element indicates
        success, and the second provides status.
    """
    env_id = database.get_element_ID("environments", env_name)
    if not env_id:
        return [False, "no env"]

    if elem_type == "websites":
        if not verify_URL(url, "website"):
            url = f"https://{url}"
            if not verify_URL(url, "website"):
                return [False, "invalid_url"]
    else:
        url = url.replace("\\", "/")
        if not verify_URL(url, "file"):
            return [False, "file not found"]

    name = url[url.rfind("/") + 1:]

    elem_id = database.get_element_ID(elem_type, name)

    if not elem_id:
        return element_not_exists(elem_type, env_id, elem_id, name, url)
    else:
        res = database.insert_env_elem(elem_type, env_id, elem_id)
        return [res, "insertion attempt"]


def element_not_exists(elem_type: str, env_id: int, elem_id: int, name: str, url: str) -> list[bool, str]:
    """Inserts an element into the specified environment if it does not
    already exist.

    Args:
        env_id (int): ID of the environment in the database.
        elem_id (int): ID of the element in the database.
        elem_type (str): Element type ("files" or "websites").
        name (str): Name of the element to insert.
        url (str): URL or path of the element.

    Returns:
        list[bool, str]: A list where the first element indicates success, and
        the second provides a status message.
    """
    database.insert_elem(elem_type, name, url)
    elem_id = database.get_element_ID(elem_type, name)
    database.insert_env_elem(elem_type, env_id, elem_id)
    return [True, "insertion attempt"]


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


def delete_env_validation(env_name: str) -> bool:
    """Validates that an environment with a specific name exists before
    deleting it from the database.

    Args:
        env_name (str): Name of the environment.

    Returns:
        bool: Returns True if the environment was successfully deleted.
              Returns False if the environment does not exist.
    """
    env_id = database.get_element_ID("environments", env_name)

    if not env_id:
        return False

    database.delete_environment(env_id)
    return True


def delete_elem_validation(env_name: str, elem_type: str, name: str) -> list[bool, str]:
    """Validates that an element exists in a specific environment before
    deleting it from the database.

    Args:
        env_name (str): Name of the environment.
        elem_type (str): Element type ("websites", "applications", or "files").
        name (str): Name of the element.

    Returns:
        bool: Returns True if the element was successfully deleted.
              Returns False if the deletion failed (e.g., if there is no
              environment or element with the specified name).
    """
    env_id = database.get_element_ID("environments", env_name)
    if not env_id:
        return [False, "no env"]

    elem_id = database.get_element_ID(elem_type, name)
    if not elem_id:
        return [False, "no elem"]

    database.delete_element(elem_type, env_id, elem_id)
    return [True, "success"]
