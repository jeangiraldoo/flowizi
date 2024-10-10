import json
import os
from src.elements.file import File
from src.elements.website import Website
from src.elements.environment import Environment
from src.system_detection.system_information import json_dir, json_path


class JSON_repository():
    def __init__(self):
        self.name = "data.json"
        self.directory = json_dir
        self.path = json_path
        self.verify_file_exists()
        self.open_JSON()

    def open_JSON(self):
        with open(self.path, "r") as file:
            self.data = json.load(file)

    def verify_file_exists(self):
        if not os.path.exists(self.directory):
            os.makedirs(self.directory)
        if not os.path.exists(self.path):
            with open(self.path, "w") as file:
                file.write("[]")

    def write_JSON(self):
        with open(self.path, 'w') as file:
            json.dump(self.data, file, indent=4)

    def verify_environment_recording(self, option: bool, environment_name) -> bool:
        """Checks if the 'record' attribute in a given environment has the same boolean value as
        the value the user wants to set. Returns True if the value in the attribute is different"""

        for environment in self.data:
            if environment["name"] == environment_name and environment["record"] != option:
                return True
        return False

    def exists_environment(self, environment_name: str) -> bool:
        """Checks if there's an environment with the specified name"""

        for environment in self.data:
            if environment["name"] == environment_name:
                return True
        return False

    def exists_environment_element(self, environment_name: str, attribute: str, element_name: str) -> bool:
        """Checks if there's an element with a specified name in a specific environment"""
        pos = self.get_environment_pos(environment_name)

        environment = self.data[pos]
        for env in environment[attribute]:
            if env["name"] == element_name:
                return True
        return False

    def get_environment_pos(self, environment_name: str) -> int:
        """Get the index of a serialized environment in the JSON file"""

        for inx, environment in enumerate(self.data):
            if environment["name"] == environment_name:
                return inx

    def add_environment(self, environment_name):
        """Serializes an Environment instance and writes it to the JSON file"""
        env_data = {"name":environment_name, "record": False, "files": [], "applications": [], "websites": []}
        self.data.append(env_data)

        self.write_JSON()

    def remove_environment(self, environment_name: str):
        """Removes a seralized Environment instance from the JSON file"""
        new_values = []
        for environment in self.data:
            if environment["name"] != environment_name:
                new_values.append(environment)
        self.data = new_values
        self.write_JSON()
        print(f"Environment {environment_name} removed successfully!")

    def add_environment_element(self, environment_name: str, attribute: str, attribute_object):
        """Adds an element to a specific environment"""

        for environment in self.data:
            if environment["name"] == environment_name:
                environment[attribute].append(attribute_object)

        self.write_JSON()

    def remove_environment_element(self, environment_name: str, attribute: str, element_name):
        """Removes an serialized Element instance from a serialized Environment instance from the JSON file"""
        new_values = []
        pos = self.get_environment_pos(environment_name)
        environment = self.data[pos]

        for hashmap in environment[attribute]:
            if hashmap["name"] != element_name:
                new_values.append(hashmap)

        environment[attribute] = new_values
        self.data[pos] = environment

        self.write_JSON()
        print(f"The element was removed from the {environment_name} environment")

    def update_environment_record(self, option: bool, environment_name):
        """Modifies the 'record' attribute in a given environment"""
        pos = self.get_environment_pos(environment_name)
        environment = self.data[pos]
        environment["record"] = option
        self.data[pos] = environment

        self.write_JSON()

    def load(self):
        environment_list = []
        for i in self.data:
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
