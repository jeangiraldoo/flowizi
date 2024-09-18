import os
import platform
import webbrowser
import json
import meetings
from config import setup


class lazyMeetings:
    version = "0.0.0"
    config_name = "data.json"
    meeting_list: list[meetings] = []

    def __init__(self):
        operative_system = platform.system()
        self.os_name = operative_system 
        self.user = os.getlogin()

        if operative_system == "Windows":
            self.config_directory = f"C:/Users/{self.user}/AppData/Local/lazyMeetings"
        self.config_path = f"{self.config_directory}/{self.config_name}"
        setup.create_config(self.config_directory, self.config_path)
        self.load_meetings()

    def exists_meeting_list(self, meeting_name):
        for i in self.meeting_list:
            if i.name == meeting_name:
                return True
        return False

    def add_meeting(self, meeting):
        data = {"name":meeting.name, "link":meeting.link}
        with open(self.config_path, "r") as file:
            meeting_data = json.load(file)
        meeting_data.append(data)
        with open(self.config_path, 'w') as file:
            json.dump(meeting_data, file, indent=4)

    def remove_meeting(self, meeting_name):
        new_values = []
        with open(self.config_path, "r") as file:
            data = json.load(file)
        for i in data:
            if i["name"] != meeting_name:
                new_values.append(i)

        with open(self.config_path, "w") as file:
            json.dump(new_values, file, indent = 4)

        print(f"Meeting {meeting_name} removed successfully!")
    
    def load_meetings(self):
        data = ""
        with open(self.config_path, 'r') as file:
            data = json.load(file)
        for i in data:
            name = i["name"]
            link = i["link"]
            self.meeting_list.append(meetings.meeting(name, link))

    def join_meeting(self, meeting_name):
        for i in self.meeting_list:
            if i.name == meeting_name:
                webbrowser.open(i.link)
                break

lazyMeetings = lazyMeetings()

