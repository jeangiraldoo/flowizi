import os
import re
from enum import Enum
from tld import get_tld
from urllib.parse import urlparse
from core.elements.environment import Environment
from core.database import database


class ResultType(Enum):
    INVALID_NUMBER = 1
    SUCCESSFUL_OPERATION = 2
    UNSUCCESSFUL_OPERATION = 3
    ENV_EXISTS = 4
    ENV_NOT_EXISTS = 5
    ELEM_NOT_EXISTS = 6
    APP_NOT_EXISTS = 7
    INVALID_URL = 8
    NO_EXECUTABLES = 9


class Validations():
    @staticmethod
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


    @staticmethod
    def add_elem_validation(env_name: str, elem_type: str, url: str) -> ResultType:
        """Validates if an element can be inserted into the database based or not.

        Args:
            env_name (str): Name of the environment to add the element to.
            elem_type (str): Type of element (e.g., "websites" or "files").
            url (str): URL or path of the element.

        Returns:
            ResultType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = database.get_element_ID("environments", env_name)
        if not env_id:
            return ResultType.ENV_NOT_EXISTS

        if elem_type == "websites":
            if not Validations.verify_URL(url, "website"):
                url = f"https://{url}"
                if not Validations.verify_URL(url, "website"):
                    return ResultType.INVALID_URL
        else:
            url = url.replace("\\", "/")
            if not Validations.verify_URL(url, "file"):
                return ResultType.INVALID_URL

        name = url[url.rfind("/") + 1:]

        elem_id = database.get_element_ID(elem_type, name)

        if not elem_id:
            return Validations.element_not_exists(elem_type, env_id, elem_id, name, url)
        else:
            if database.insert_env_elem(elem_type, env_id, elem_id):
                return ResultType.SUCCESSFUL_OPERATION
            else:
                return ResultType.UNSUCCESSFUL_OPERATION


    @staticmethod
    def element_not_exists(elem_type: str, env_id: int, elem_id: int, name: str, url: str) -> ResultType:
        """Inserts an element into the specified environment if it does not
        already exist.

        Args:
            env_id (int): ID of the environment in the database.
            elem_id (int): ID of the element in the database.
            elem_type (str): Element type ("files" or "websites").
            name (str): Name of the element to insert.
            url (str): URL or path of the element.

        Returns:
            ResultType: Enum indicating that the operation was successful.

        """
        database.insert_elem(elem_type, name, url)
        elem_id = database.get_element_ID(elem_type, name)
        database.insert_env_elem(elem_type, env_id, elem_id)
        return ResultType.SUCCESSFUL_OPERATION


    @staticmethod
    def verify_URL(url: str, element_type: str) -> bool:
        "Checks if a URL is valid"
        if element_type == "website":
            return Validations.verify_website_url(url)
        elif element_type == "file":
            return Validations.verify_file_url(url)


    @staticmethod
    def verify_website_url(url) -> bool:
        parsed_url = urlparse(url)
        scheme = parsed_url.scheme
        netloc = parsed_url.netloc
        if not scheme and not netloc:
            return False

        if not Validations.has_valid_tld(url):
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


    @staticmethod
    def has_valid_tld(url: str) -> bool:
        # If the URL doesn't have a scheme (protocol), add "http://"
        try:
            get_tld(url, fail_silently=False)  # Attempt to parse the TLD
            return True
        except ValueError:
            return False


    @staticmethod
    def verify_file_url(url) -> bool:
        if not os.path.exists(url):
            return False
        return True


    @staticmethod
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


    @staticmethod
    def delete_elem_validation(env_name: str, elem_type: str, name: str) -> ResultType:
        """Validates that an element exists in a specific environment before
        deleting it from the database.

        Args:
            env_name (str): Name of the environment.
            elem_type (str): Element type ("websites", "applications", or "files").
            name (str): Name of the element.

        Returns:
            ResultType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = database.get_element_ID("environments", env_name)
        if not env_id:
            return ResultType.ENV_NOT_EXISTS

        elem_id = database.get_element_ID(elem_type, name)
        if not elem_id:
            return ResultType.ELEM_NOT_EXISTS

        database.delete_element(elem_type, env_id, elem_id)
        return ResultType.SUCCESSFUL_OPERATION


    @staticmethod
    def env_exists(env_name: str) -> bool:
        """Checks if an environment exists in the database.

        Acts as an interface between the request and the database by
        verifying if the specified environment is present.

        Args:
            env_name (str): The name of the environment to check.

        Returns:
            bool: True if the environment exists, False otherwise.
        """
        if database.get_element_ID("environments", env_name):
            return True
        return False


    @staticmethod
    def get_envs() -> list[Environment]:
        """Returns a list of Environment instances, each containing its respective
        elements.

        Retrieves and deserializes environment data from the database to
        construct Environment instances with their contained elements.

        Returns:
            list[Environment]: A list of deserialized Environment instances.
        """
        return database.deserialize_elems()
