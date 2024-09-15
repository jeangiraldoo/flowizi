import os
import platform
import configparser

class lazyMeetings:
    parser = configparser.ConfigParser()
    version = "0.0.0"
    config_name = "config.ini"

    def __init__(self):
        operative_system = platform.system()
        self.os_name = operative_system 
        self.user = os.getlogin()

        if(operative_system == "Windows"):
            self.config_directory = f"C:/Users/{self.user}/AppData/Local/lazyMeetings"
        self.config_path = f"{self.config_directory}/{self.config_name}"

lazyMeetings = lazyMeetings()

