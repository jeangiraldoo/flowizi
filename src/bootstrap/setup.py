import os
import platform
import configparser

os_name = platform.system()
user_name = os.getlogin()


def verify_path_exists(path) -> bool:
    if os.path.exists(path):
        return True 
    return False

def create_json(directory, json_path):
    """Create the configuration file that lazyMeetings will use"""
    if not(verify_path_exists(directory)):
        os.makedirs(directory) 
    if not(verify_path_exists(json_path)):
        with open(json_path, "w") as file:
            file.write("[]")
