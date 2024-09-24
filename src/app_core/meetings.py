from src.app_core.online_element import OnlineElement
import webbrowser

class Meeting(OnlineElement):
    def __init__(self, name, link):
        self.name = name
        self.link = link

    def get_name(self):
        return name

    def get_link(self):
        return link
