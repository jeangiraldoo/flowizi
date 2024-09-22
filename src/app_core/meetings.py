from src.app_core.element import Element

class meeting(Element):
    link = ""
    time = ""

    def __init__(self, name, link):
        self.name = name
        self.link = link
        self.time = time

    def get_name(self):
        return name

    def get_link(self):
        return link

