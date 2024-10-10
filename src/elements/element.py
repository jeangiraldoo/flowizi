from abc import ABC


class Element(ABC):
    def __init__(self, name):
        self.name = name
