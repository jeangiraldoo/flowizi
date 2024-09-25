class Environment():
    def __init__(self, name):
        self.name = name
        self.applications = []
        self.meetings = []
        self.websites = []

    def add_element(self, element_type, element):
        env_list = getattr(self, element_type)
        env_list.append(element)

    def element_exists(self, element_type: str, element_name: str):
        env_list = getattr(self, element_type)
        return any(element_name == element.name for element in env_list)
    
    def remove_element(self, element_type: str, element_name):
        env_list = getattr(self, element_type)
        env_list = [element for element in env_list if element.name != element_name]
        print(f"{element_name} was removed successfully from the {self.name} environment")

    def list_elements(self, element_type: str, element_name):
        env_list = getattr(self, element_type)
        name_list = [element.name for element in env_list]
        print("\n".join(name_list))

    def list_all_elements(self):
        list_elements("applications")
        list_elements("meetings")

    def start(self):
        for meeting in self.meetings:
            meeting.start()
        for website in self.websites:
            website.start()
