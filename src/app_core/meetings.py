from src.app_core.element import Element

class Meeting(Element):

    def __init__(self, name, link):
        self.name = name
        self.link = link

    def get_name(self):
        return name

    def get_link(self):
        return link

    def join_meeting(self, meeting_name):
        for i in self.meeting_list:
            if i.name == meeting_name:
                webbrowser.open(i.link)
                break    
