import os
import platform
import webbrowser
import json
from urllib.parse import urlparse
from src.app_core.environment import Environment
from src.app_core.website import Website
from src.app_core.file import File
from src.bootstrap import setup


class Flowizi:
    version = "1.4.0-alpha"
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

    def verify_environment_recording(self, option: bool, environment_name) -> bool:
        """Checks if the 'record' attribute in a given environment has the same boolean value as
        the value the user wants to set. Returns True if the value in the attribute is different"""
        pos = self.get_environment_pos(environment_name) 
        environment = self.environment_list[pos]
        if environment.record != option:
            return True
        return False

    def verify_URL(self, url: str, element_type: str) -> bool:
        "Checks if a URL is valid"
        if element_type == "website":
            parsed_url = urlparse(url)
            if not(all([parsed_url.scheme, parsed_url.netloc])):
                return False
        elif element_type == "file":
            if not os.path.exists(url):
                return False
        return True

    def obj_to_dict(self, obj):
        return {"name":obj.name, "url":obj.url} 

    def exists_environment_list(self, environment_name: str) -> bool:
        """Checks if there's an environment with the specified name"""
        for environment in self.environment_list:
            if environment.name == environment_name:
                return True
        return False

    def exists_environment_element(self, environment_name: str, attribute: str, element_name: str) -> bool:
        """Checks if there's an element with a specified name in a specific environment"""
        pos = self.get_environment_pos(environment_name)

        with open(self.config_path, "r") as file:
            data = json.load(file)

        environment = data[pos]
        for env in environment[attribute]:
            if env["name"] == element_name:
                return True
        return False

    def get_environment_pos(self, environment_name: str) -> int:
        """Get the index of a serialized environment in the JSON file"""
        for index, environment in enumerate(self.environment_list):
            if environment.name == environment_name:
                return index

    def add_environment(self, environment):
        """Serializes an Environment instance and writes it to the JSON file""" 
        data = {"name":environment.name, "record":environment.record, "files": environment.files, "applications":environment.applications, "websites":environment.websites}
        with open(self.config_path, "r") as file:
            environment_data = json.load(file)
        environment_data.append(data)
        with open(self.config_path, 'w') as file:
            json.dump(environment_data, file, indent=4)

    def remove_environment(self, environment_name: str):
        """Removes a seralized Environment instance from the JSON file"""
        new_values = []
        with open(self.config_path, "r") as file:
            data = json.load(file)
        for environment in data:
            if environment["name"] != environment_name:
                new_values.append(environment)

        with open(self.config_path, "w") as file:
            json.dump(new_values, file, indent = 4)

        print(f"Environment {environment_name} removed successfully!")

    def add_environment_element(self, environment_name: str, attribute: str, attribute_object):
        """Adds an element to a specific environment"""
        with open(self.config_path, "r") as file:
            data = json.load(file)
        for environment in data:
            if environment["name"] == environment_name:
                environment[attribute].append(self.obj_to_dict(attribute_object))

        with open(self.config_path, "w") as file:
            json.dump(data, file, indent = 4)

    def remove_environment_element(self, environment_name: str, attribute: str, element_name):
        """Removes an serialized Element instance from a serialized Environment instance from the JSON file"""
        with open(self.config_path, "r") as file:
            data = json.load(file)
        new_values = []
        pos = self.get_environment_pos(environment_name)
        environment = data[pos]

        for hashmap in environment[attribute]:
            if hashmap["name"] != element_name:
                new_values.append(hashmap)

        environment[attribute] = new_values
        data[pos] = environment

        with open(self.config_path, "w") as file:
            json.dump(data, file, indent = 4)

        print(f"The element was removed from the {environment_name} environment")

    def update_environment_record(self, option: bool, environment_name):
        """Modifies the 'record' attribute in a given environment"""
        with open(self.config_path, "r") as file:
            data = json.load(file)
        pos = self.get_environment_pos(environment_name)
        environment = data[pos]
        environment["record"] = option
        data[pos] = environment

        with open(self.config_path, "w") as file:
            json.dump(data, file, indent = 4)

    def load_environments(self):
        data = ""
        with open(self.config_path, 'r') as file:
            data = json.load(file)
        for i in data:
            name = i["name"]
            record: bool = i["record"]
            websites = i["websites"]
            files = i["files"]
            new_environment = Environment(name)
            for dictionary in websites:
                new_website = Website(dictionary["name"], dictionary["url"])
                new_environment.websites.append(new_website)

            for dictionary in files:
                new_file = File(dictionary["name"], dictionary["url"])
                new_environment.files.append(new_file)

            if record != False:
                new_environment.set_record(True)
            self.environment_list.append(new_environment)
                    
flowizi = Flowizi()

