import webbrowser
from src.app_core.element import Element

class OnlineElement(Element):
    def __init__(self, name: str, link: str):
        super().__init__(name)
        self.link = link

    def start(self):
       webbrowser.open(self.link) 