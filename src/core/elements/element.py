from abc import ABC
from enum import Enum


class ElementType(Enum):
    ENV = "environments"
    WEBSITE = "websites"
    APP = "applications"
    FILE = "files"


class Element(ABC):
    def __init__(self, name):
        self.name = name
