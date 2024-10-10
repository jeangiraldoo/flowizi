from src.elements.contained_element import ContainedElement
import subprocess
import os


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
