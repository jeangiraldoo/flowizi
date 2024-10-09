import json
import platform
import os
from src.app_core.file import File
from src.app_core.website import Website
from src.app_core.environment import Environment


class JSON_repository():
    def __init__(self):
        self.name = "data.json"
        os_name = platform.system()
        user = os.getlogin()

        if os_name == "Windows":
            self.directory = f"C:/Users/{user}/AppData/Local/flowizi"
        self.path = f"{self.directory}/{self.name}"

        if not(os.path.exists(self.directory)):
            os.makedirs(self.directory) 
        if not(os.path.exists(self.path)):
            with open(self.path, "w") as file:
                file.write("[]")


    def verify_environment_recording(self, option: bool, environment_name) -> bool:
        """Checks if the 'record' attribute in a given environment has the same boolean value as
        the value the user wants to set. Returns True if the value in the attribute is different"""
        with open(self.path, "r") as file:
            data = json.load(file)

        for environment in data:
            if environment["name"] == environment_name and environment["record"] != option:
                return True
        return False

    def exists_environment(self, environment_name: str) -> bool:
        """Checks if there's an environment with the specified name"""
        with open(self.path, "r") as file:
            data = json.load(file)

        for environment in data:
            if environment["name"] == environment_name:
                return True
        return False

    def exists_environment_element(self, environment_name: str, attribute: str, element_name: str) -> bool:
        """Checks if there's an element with a specified name in a specific environment"""
        pos = self.get_environment_pos(environment_name)

        with open(self.path, "r") as file:
            data = json.load(file)

        environment = data[pos]
        for env in environment[attribute]:
            if env["name"] == element_name:
                return True
        return False

    def get_environment_pos(self, environment_name: str) -> int:
        """Get the index of a serialized environment in the JSON file"""

        with open(self.path, "r") as file:
            data = json.load(file)
        for inx, environment in enumerate(data):
            if environment["name"] == environment_name:
                return inx

    def obj_to_dict(self, obj):
        return {"name":obj.name, "url":obj.url}

    def add_environment(self, environment):
        """Serializes an Environment instance and writes it to the JSON file""" 
        data = {"name":environment.name, "record":environment.record, "files": environment.files, "applications":environment.applications, "websites":environment.websites}
        with open(self.path, "r") as file:
            environment_data = json.load(file)
        environment_data.append(data)
        with open(self.path, 'w') as file:
            json.dump(environment_data, file, indent=4)

    def remove_environment(self, environment_name: str):
        """Removes a seralized Environment instance from the JSON file"""
        new_values = []
        with open(self.path, "r") as file:
            data = json.load(file)
        for environment in data:
            if environment["name"] != environment_name:
                new_values.append(environment)

        with open(self.path, "w") as file:
            json.dump(new_values, file, indent = 4)

        print(f"Environment {environment_name} removed successfully!")

    def add_environment_element(self, environment_name: str, attribute: str, attribute_object):
        """Adds an element to a specific environment"""
        with open(self.path, "r") as file:
            data = json.load(file)
        for environment in data:
            if environment["name"] == environment_name:
                environment[attribute].append(self.obj_to_dict(attribute_object))

        with open(self.path, "w") as file:
            json.dump(data, file, indent = 4)

    def remove_environment_element(self, environment_name: str, attribute: str, element_name):
        """Removes an serialized Element instance from a serialized Environment instance from the JSON file"""
        with open(self.path, "r") as file:
            data = json.load(file)
        new_values = []
        pos = self.get_environment_pos(environment_name)
        environment = data[pos]

        for hashmap in environment[attribute]:
            if hashmap["name"] != element_name:
                new_values.append(hashmap)

        environment[attribute] = new_values
        data[pos] = environment

        with open(self.path, "w") as file:
            json.dump(data, file, indent = 4)

        print(f"The element was removed from the {environment_name} environment")

    def update_environment_record(self, option: bool, environment_name):
        """Modifies the 'record' attribute in a given environment"""
        with open(self.path, "r") as file:
            data = json.load(file)
        pos = self.get_environment_pos(environment_name)
        environment = data[pos]
        environment["record"] = option
        data[pos] = environment

        with open(self.path, "w") as file:
            json.dump(data, file, indent = 4)

    def load(self):
        data = ""
        environment_list = []
        with open(self.path, 'r') as file:
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
            environment_list.append(new_environment)
        return environment_list
