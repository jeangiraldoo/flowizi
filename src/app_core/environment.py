from src.app_core.screen_recorder import ScreenRecorder


class Environment():
    def __init__(self, name):
        self.name = name
        self.record = False
        self.applications = []
        self.websites = []
        self.files = []

    def set_record(self, setting):
        self.record = setting

    def start(self):
        for website in self.websites:
            website.start()
        for file in self.files:
            file.start()
        if self.record:
            ScreenRecorder.start_recording(self.name)
