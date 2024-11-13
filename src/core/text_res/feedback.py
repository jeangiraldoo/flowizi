from enum import Enum
from core.platform.info import lang
from core.text_res.langs import english


def _get_feedback(feedback_type):
    if lang == "en":
        return english.MSGS[feedback_type]


class Feedback(Enum):
    ENV_NOT_EXISTS = _get_feedback("Env not exists")
    ENV_ALREADY_EXISTS = _get_feedback("Env already exists")
    ENVIRONMENT_SUCCESS = _get_feedback("Env success")

    WEBSITE_INVALID_URL = _get_feedback("Website invalid URL")
    WEBSITE_ALREADY_EXISTS = _get_feedback("Website already exists")
    WEBSITE_SUCCESS = _get_feedback("Website success")

    FILE_NOT_FOUND = _get_feedback("File not found")
    FILE_ALREADY_EXISTS = _get_feedback("File already exists")
    FILE_SUCCESS = _get_feedback("File success")

    APP_SUCCESS = _get_feedback("App success")
    NO_SIMILAR_APP_NAME = _get_feedback("No similar app name")

    NO_EXECUTABLES = _get_feedback("No executables")

    NUMBER_OUT_OF_BOUNDS = _get_feedback("Number out of bounds")

    ELEMENT_ALREADY_EXISTS = _get_feedback("Element already exists")
