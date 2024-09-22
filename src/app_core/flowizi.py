import os
import platform
import webbrowser
import json
from app_core import meetings
from bootstrap import setup


class flowizi:
    version = "0.1.0-alpha"
    config_name = "data.json"
    meeting_list: list[meetings] = []

    def __init__(self):
        operative_system = platform.system()
        self.os_name = operative_system 
        self.user = os.getlogin()

        if operative_system == "Windows":
            self.config_directory = f"C:/Users/{self.user}/AppData/Local/flowizi"
        self.config_path = f"{self.config_directory}/{self.config_name}"
        setup.create_json(self.config_directory, self.config_path)
        self.load_meetings()

    def exists_meeting_list(self, meeting_name):
        for i in self.meeting_list:
            if i.name == meeting_name:
                return True
        return False

    def add_meeting(self, meeting):
        data = {"name":meeting.name, "link":meeting.link, "time":meeting.time}
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

    def update_meeting(self, meeting_name, attribute, value):
        with open(self.config_path, "r") as file:
            data = json.load(file)
        for i in data:
            if i["name"] == meeting_name and attribute == "time" and self.validate_time(value):
                i[attribute] = value

        with open(self.config_path, "w") as file:
            json.dump(data, file, indent = 4)

    def validate_time(self, time):
        if time.find(":") == -1:
            print("Minutes should be separated from seconds by a ':'")
            return False
        
        time_split = time.split(":")
        minutes = time_split[0]
        seconds = time_split[1]
                        
        try:
            int(minutes)
        except ValueError:
            print("Minutes should be numbers")
            return False

        try:
            int(seconds)
        except ValueError:
            print("Seconds should be numbers")
            return False

        if len(minutes) > 2 or len(seconds) > 2:
            print("Parts of the time should not be formed by more than 2 numbers")
            return False

        if int(minutes) < 0 or int(minutes) > 24:
            print("Minutes should be between 0 and 24")
            return False
        if int(seconds) < 0 or int(seconds) > 59:
            print("Seconds should be between 0 and 59")
            return False
            
        return True

    def load_meetings(self):
        data = ""
        with open(self.config_path, 'r') as file:
            data = json.load(file)
        for i in data:
            name = i["name"]
            link = i["link"]
            time = i["time"]
            new_meeting = meetings.meeting(name, link, time)
            self.meeting_list.append(new_meeting)

    def join_meeting(self, meeting_name):
        for i in self.meeting_list:
            if i.name == meeting_name:
                webbrowser.open(i.link)
                break

flowizi = flowizi()

