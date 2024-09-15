import os
import configparser
from app_data import lazyMeetings

def remove_path_value(app_name: str):
    """Remove an existing key/value pair in the Path section of the configuration file

    Parameters: 
    app_name(str): Name of the app, represented as a key
    """
    file = open(lazyMeetings.config_path, "w")
    lazyMeetings.parser.remove_option("Meetings", app_name)
    lazyMeetings.parser.write(file)
    print(f"{app_name} removed successfully!")

def add_path_value(app_name, app_path):
    lazyMeetings.parser.read(lazyMeetings.config_path)
    lazyMeetings.parser["Meetings"][app_name] = app_path
            
    file = open(lazyMeetings.config_path, "w")
    lazyMeetings.parser.write(file)
    print(f"{app_name} added successfully!")

def add_setting(setting_name: str):
    """Create a setting that will be stored in the configuration file

    Parameters:
    setting_name(str): This name will be added to the configuration file in the last line as 'setting_name = []'
    """
    lazyMeetings.parser[setting_name] = {}
    file = open(lazyMeetings.config_path, "w")
    lazyMeetings.parser.write(file)

def verify_path_exists(path) -> bool:
    if(os.path.exists(path)):
        return True 
    return False

def read_config() -> list[str]:
    lazyMeetings.parser.read(lazyMeetings.config_path)

def create_config():
    """Create the configuration file that lazyMeetings will use"""
    if(not(verify_path_exists(lazyMeetings.config_directory))):
        os.makedirs(lazyMeetings.config_directory) 
    if(not(verify_path_exists(lazyMeetings.config_path))):
        open(lazyMeetings.config_path, "w")
        add_setting("Meetings")

