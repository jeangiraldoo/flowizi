import os
from urllib.parse import urlparse
from core.database import validations


class Flowizi:
    def __init__(self):
        self.version = "1.4.0-alpha"
        self.environment_list = validations.get_envs()

    def update_environments(self):
        """Gets the current environments in the database and updates
        the environment_list attribute"""
        self.environment_list = validations.get_envs()

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
