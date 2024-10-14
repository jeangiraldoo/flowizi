import os
from urllib.parse import urlparse
from json_data.json_repository import JSON_repository


class Flowizi:
    def __init__(self):
        self.version = "1.4.0-alpha"
        self.json = JSON_repository()
        self.environment_list = self.json.load()

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
