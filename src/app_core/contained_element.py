import webbrowser
from abc import ABC, abstractmethod
from src.app_core.element import Element

class ContainedElement(Element):
    def __init__(self, name: str, url: str):
        super().__init__(name)
        self.url = url
    
    @abstractmethod
    def start(self):
        pass
