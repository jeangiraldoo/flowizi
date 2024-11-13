import os
import re
from enum import Enum
from tld import get_tld
from urllib.parse import urlparse
from core.elements.element import ElementType, Environment
from core.database._queries import Query


class ResultType(Enum):
    INVALID_NUMBER = 1
    SUCCESSFUL_OPERATION = 2
    UNSUCCESSFUL_OPERATION = 3
    ENV_ALREADY_EXISTS = 4
    ENV_NOT_EXISTS = 5
    ELEM_NOT_EXISTS = 6
    APP_NOT_EXISTS = 7
    INVALID_URL = 8
    NO_EXECUTABLES = 9
    INVALID_FILE_PATH = 10
    ENV_CREATED = 11


class Validations():
    @staticmethod
    def add_env_validation(env_name: str) -> ResultType:
        """Validates if an environment can be inserted into the database.

        Args:
            env_name (Str): Name of the environment to add.
        Returns:
            ResultType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = Query.get_element_ID(ElementType.ENV, env_name)
        if env_id:
            return ResultType.ENV_ALREADY_EXISTS

        Query.add_environment(env_name)
        return ResultType.ENV_CREATED

    @staticmethod
    def add_elem_validation(env_name: str, elem_type: ElementType, url: str) -> ResultType:
        """Validates if an element can be inserted into the database based or not.

        Args:
            env_name (str): Name of the environment to add the element to.
            elem_type (ElementType): Type of element (e.g., WEBSITE or FILE).
            url (str): URL or path of the element.

        Returns:
            ResultType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = Query.get_element_ID(ElementType.ENV.value, env_name)
        if not env_id:
            return ResultType.ENV_NOT_EXISTS

        url, result = Validations._validate_url(elem_type, url)
        if not result == ResultType.SUCCESSFUL_OPERATION:
            return result

        name = url[url.rfind("/") + 1:]

        elem_id = Query.get_element_ID(elem_type.value, name)

        if not elem_id:
            return Validations.element_not_exists(elem_type, env_id, elem_id, name, url)
        elif Query.insert_env_elem(elem_type.value, env_id, elem_id):
            return ResultType.SUCCESSFUL_OPERATION
        else:
            return ResultType.UNSUCCESSFUL_OPERATION


    @staticmethod
    def _validate_url(elem_type, url):
        if elem_type == ElementType.WEBSITE:
            if not Validations._verify_website_url(url, ElementType.WEBSITE):
                url = f"https://{url}"
                if not Validations._verify_website_url(url):
                    return url, ResultType.INVALID_URL
        else:
            url = url.replace("\\", "/")
            if not Validations.verify_file_url(url):
                return url, ResultType.INVALID_FILE_PATH

        return url, ResultType.SUCCESSFUL_OPERATION

    @staticmethod
    def element_not_exists(elem_type: ElementType, env_id: int, elem_id: int, name: str, url: str) -> ResultType:
        """Inserts an element into the specified environment if it does not
        already exist.

        Args:
            env_id (int): ID of the environment in the database.
            elem_id (int): ID of the element in the database.
            elem_type (ElementType): Element type (FILE or WEBSITE).
            name (str): Name of the element to insert.
            url (str): URL or path of the element.

        Returns:
            ResultType: Enum indicating that the operation was successful.

        """
        Query.insert_elem(elem_type.value, name, url)
        elem_id = Query.get_element_ID(elem_type.value, name)
        Query.insert_env_elem(elem_type.value, env_id, elem_id)
        return ResultType.SUCCESSFUL_OPERATION

    @staticmethod
    def _verify_website_url(url) -> bool:
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
    def _verify_file_url(url) -> bool:
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
        env_id = Query.get_element_ID(ElementType.ENV.value, env_name)

        if not env_id:
            return False

        Query.delete_environment(env_id)
        return True

    @staticmethod
    def delete_elem_validation(env_name: str, elem_type: ElementType, name: str) -> ResultType:
        """Validates that an element exists in a specific environment before
        deleting it from the database.

        Args:
            env_name (str): Name of the environment.
            elem_type (ElementType): Element type (WEBSITE, APP, or FILE).
            name (str): Name of the element.

        Returns:
            ResultType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = Query.get_element_ID(elem_type.ENV.value, env_name)
        if not env_id:
            return ResultType.ENV_NOT_EXISTS

        elem_id = Query.get_element_ID(elem_type.value, name)
        if not elem_id:
            return ResultType.ELEM_NOT_EXISTS

        Query.delete_element(elem_type.value, env_id, elem_id)
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
        if Query.get_element_ID(ElementType.ENV.value, env_name):
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
        return Query.deserialize_elems()
