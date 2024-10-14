import os
from elements.contained_element import ContainedElement


class Application(ContainedElement):
    def __init__(self, name: str, url: str):
        super().__init__(name, url)

    def start(self):
        try:
            os.startfile(self.url)
        except Exception as e:
            print(f"Could not open {self.url}: {e}")
