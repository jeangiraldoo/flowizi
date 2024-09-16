import os
import configparser

def verify_path_exists(path) -> bool:
    if(os.path.exists(path)):
        return True 
    return False

def create_config(directory, path):
    """Create the configuration file that lazyMeetings will use"""
    if(not(verify_path_exists(directory))):
        os.makedirs(directory) 
    if(not(verify_path_exists(path))):
        with open(path, "w") as file:
            file.write("[]")

