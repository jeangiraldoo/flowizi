import os
import platform
import webbrowser
import json
from src.app_core import environment
from src.app_core.meetings import Meeting
from src.app_core.website import Website
from src.bootstrap import setup


class flowizi:
    version = "0.1.0-alpha"
    config_name = "data.json"
    environment_list = []

    def __init__(self):
        operative_system = platform.system()
        self.os_name = operative_system 
        self.user = os.getlogin()

        if operative_system == "Windows":
            self.config_directory = f"C:/Users/{self.user}/AppData/Local/flowizi"
        self.config_path = f"{self.config_directory}/{self.config_name}"
        setup.create_json(self.config_directory, self.config_path)
        self.load_environments()

    def obj_to_dict(self, obj):
        return {"name":obj.name, "link":obj.link} 

    def exists_environment_list(self, meeting_name):
        for environment in self.environment_list:
            if environment.name == meeting_name:
                return True
        return False

    def add_environment(self, environment):
        data = {"name":environment.name, "applications":environment.applications, "meetings":environment.meetings, "websites":environment.websites}
        with open(self.config_path, "r") as file:
            environment_data = json.load(file)
        environment_data.append(data)
        with open(self.config_path, 'w') as file:
            json.dump(environment_data, file, indent=4)

    def remove_environment(self, environment_name):
        new_values = []
        with open(self.config_path, "r") as file:
            data = json.load(file)
        for environment in data:
            if environment["name"] != environment_name:
                new_values.append(environment)

        with open(self.config_path, "w") as file:
            json.dump(new_values, file, indent = 4)

        print(f"Environment {environment_name} removed successfully!")

    def add_environment_element(self, environment_name, attribute, attribute_object):
        with open(self.config_path, "r") as file:
            data = json.load(file)
        for environment in data:
            if environment["name"] == environment_name:
                environment[attribute].append(self.obj_to_dict(attribute_object))

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

    def load_environments(self):
        data = ""
        with open(self.config_path, 'r') as file:
            data = json.load(file)
        for i in data:
            name = i["name"]
            meetings = i["meetings"]
            websites = i["websites"]
            new_environment = environment.Environment(name)
            for dictionary in meetings:
                new_meeting = Meeting(dictionary["name"], dictionary["link"])
                new_environment.meetings.append(new_meeting)
            for dictionary in websites:
                new_website = Website(dictionary["name"], dictionary["link"])
                new_environment.websites.append(new_website)

            self.environment_list.append(new_environment)
                    
    def join_meeting(self, meeting_name):
        for i in self.meeting_list:
            if i.name == meeting_name:
                webbrowser.open(i.link)
                break

flowizi = flowizi()

