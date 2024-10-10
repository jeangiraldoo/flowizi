import webbrowser
from src.elements.contained_element import ContainedElement


class Website(ContainedElement):
    def __init__(self, name, url):
        super().__init__(name, url)

    def start(self):
        webbrowser.open(self.url)
