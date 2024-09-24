import webbrowser
from src.app_core.element import Element

class OnlineElement(Element):
    def start(self):
       webbrowser.open(self.link) 
