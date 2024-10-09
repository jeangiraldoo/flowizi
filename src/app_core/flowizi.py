import os
import platform
import webbrowser
from urllib.parse import urlparse
from src.app_core.environment import Environment
from src.app_core.website import Website
from src.app_core.file import File
from src.app_core.json_repository import JSON_repository


class Flowizi:
    def __init__(self):
        version = "1.4.0-alpha"
        self.json = JSON_repository()
        self.environment_list = self.json.load()
        operative_system = platform.system()
        self.os_name = operative_system 
        self.user = os.getlogin()

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

flowizi = Flowizi()
