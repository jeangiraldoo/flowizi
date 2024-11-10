from abc import abstractmethod
from core.elements.element import Element
import webbrowser
import subprocess
import os


class ContainedElement(Element):
    def __init__(self, name: str, url: str):
        super().__init__(name)
        self.url = url

    @abstractmethod
    def start(self):
        pass


class Website(ContainedElement):
    def __init__(self, name, url):
        super().__init__(name, url)

    def start(self):
        webbrowser.open(self.url)


class File(ContainedElement):
    def __init__(self, name, url):
        super().__init__(name, url)

    def start(self):
        try:
            if not os.path.exists(self.url):
                raise FileNotFoundError(
                    f"Error. The {self.name} file existed when it was added,"
                    " but it can no longer be found in the original path"
                )
            subprocess.run(["start", self.url], shell = True)
        except FileNotFoundError as e:
            print(e)


class Application(ContainedElement):
    def __init__(self, name: str, url: str):
        super().__init__(name, url)

    def start(self):
        try:
            os.startfile(self.url)
        except Exception as e:
            print(f"Could not open {self.url}: {e}")
