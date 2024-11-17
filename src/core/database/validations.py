import os
import re
from enum import Enum
from tld import get_tld
from urllib.parse import urlparse
from core.elements.element import ElemType, Environment
from core.database._queries import Query


class ResType(Enum):
    INVALID_NUMBER = 1
    SUCCESS = 2
    FAILURE = 3
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
    def add_env_validation(env_name: str) -> ResType:
        """Validates if an environment can be inserted into the database.

        Args:
            env_name (Str): Name of the environment to add.
        Returns:
            ResType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = Query.get_element_ID(ElemType.ENV, env_name)
        if env_id:
            return ResType.ENV_ALREADY_EXISTS

        Query.add_environment(env_name)
        return ResType.ENV_CREATED

    @staticmethod
    def add_elem_validation(env_name: str, elem_type: ElemType, url: str) -> ResType:
        """Validates if an element can be inserted into the database based or not.

        Args:
            env_name (str): Name of the environment to add the element to.
            elem_type (ElemType): Type of element (e.g., WEBSITE or FILE).
            url (str): URL or path of the element.

        Returns:
            ResType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = Query.get_element_ID(ElemType.ENV.value, env_name)
        if not env_id:
            return ResType.ENV_NOT_EXISTS

        url, result = Validations._validate_url(elem_type, url)
        if not result == ResType.SUCCESS:
            return result

        name = url[url.rfind("/") + 1:]

        elem_id = Query.get_element_ID(elem_type.value, name)

        if not elem_id:
            return Validations._insert_if_elem_not_exists(elem_type, env_id, name, url)
        elif Query.insert_env_elem(elem_type.value, env_id, elem_id):
            return ResType.SUCCESS
        else:
            return ResType.FAILURE

    @staticmethod
    def _validate_url(elem_type: ElemType, url: str) -> tuple[str, ResType]:
        url = url.replace("\\", "/")
        if elem_type == ElemType.WEB and not (
            Validations._is_valid_website_url(url) or
            Validations._is_valid_website_url(f"https://{url}")
        ):
            return url, ResType.INVALID_URL

        if elem_type != ElemType.WEB and not Validations._is_valid_file_path(url):
            return url, ResType.INVALID_FILE_PATH

        return url, ResType.SUCCESS

    @staticmethod
    def _insert_if_elem_not_exists(elem_type: ElemType, env_id: int, name: str, url: str) -> ResType:
        """Inserts an element into the specified environment if it does not
        already exist.

        Args:
            env_id (int): ID of the environment in the database.
            elem_type (ElemType): Element type (FILE or WEBSITE).
            name (str): Name of the element to insert.
            url (str): URL or path of the element.

        Returns:
            ResType: Enum indicating that the operation was successful.

        """
        Query.insert_elem(elem_type.value, name, url)
        elem_id = Query.get_element_ID(elem_type.value, name)
        Query.insert_env_elem(elem_type.value, env_id, elem_id)
        return ResType.SUCCESS

    @staticmethod
    def _is_valid_website_url(url: str) -> bool:
        """
        Validates if the provided URL follows the appropriate format for
        a website URL.

        Args:
            url (str): The URL string to validate.

        Returns:
            bool: True if the URL follows a valid website format,
                  False otherwise.
        """
        parsed_url = urlparse(url)
        protocol: str = parsed_url.scheme  # The protocol is necessary to properly parse the URL
        domain: str = parsed_url.netloc

        if not protocol and not domain:
            return False

        try:
            get_tld(url, fail_silently=False)  # Attempt to parse the Top Level Domain
        except ValueError:
            return False

        if not re.match("[a-z]", domain[0]) or not re.match("[a-z]", domain[-1]):
            return False

        if "." not in domain or ".." in domain:
            return False

        return True

    @staticmethod
    def _is_valid_file_path(url: str) -> bool:
        """
        Checks if the provided URL corresponds to an existing path in the
        file system.

        Args:
            url (str): The URL or file system path to validate.

        Returns:
            bool: True if the URL corresponds to an existing file path,
                  False otherwise.
        """
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
        env_id = Query.get_element_ID(ElemType.ENV.value, env_name)

        if not env_id:
            return False

        Query.delete_environment(env_id)
        return True

    @staticmethod
    def delete_elem_validation(env_name: str, elem_type: ElemType, name: str) -> ResType:
        """Validates that an element exists in a specific environment before
        deleting it from the database.

        Args:
            env_name (str): Name of the environment.
            elem_type (ElemType): Element type (WEBSITE, APP, or FILE).
            name (str): Name of the element.

        Returns:
            ResType: Enum indicating the result of the validation, such as
                        whether the element was successfully inserted or if
                        errors occurred.
        """
        env_id = Query.get_element_ID(elem_type.ENV.value, env_name)
        if not env_id:
            return ResType.ENV_NOT_EXISTS

        elem_id = Query.get_element_ID(elem_type.value, name)
        if not elem_id:
            return ResType.ELEM_NOT_EXISTS

        Query.delete_element(elem_type.value, env_id, elem_id)
        return ResType.SUCCESS

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
        if Query.get_element_ID(ElemType.ENV.value, env_name):
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
