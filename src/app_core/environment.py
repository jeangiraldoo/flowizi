import pyaudio
import os
import re
import subprocess
import sounddevice
from datetime import datetime
from fuzzywuzzy import fuzz

class Environment():
    def __init__(self, name):
        self.name = name
        self.record = False
        self.applications = []
        self.websites = []

    def set_record(self, option: bool):
        self.record = option

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

    def start(self):
        if self.record:
            self.start_recording()
        for website in self.websites:
            website.start()

    def get_ffmpeg_path(self) -> str:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(package_dir, '..', "..", 'bin', 'ffmpeg_windows.exe')
        return ffmpeg_path

    def get_main_microphone(self):
        return sounddevice.query_devices(kind='input')['name']
    
    def get_ffmpeg_devices(self):
        """Returns the devices FFmpeg can detect in the computer. FFmpeg expectes to use one of these devices to record audio"""
        command = [self.get_ffmpeg_path(), "-list_devices", "true", "-f", "dshow", "-i", "dummy"]
        vale = subprocess.run(command, stderr=subprocess.PIPE, text=True, encoding = "utf-8")
        device_names = re.findall(r'"([^"]+)"', vale.stderr)
        new_list = []

        for i in range(1, len(device_names)):
            if not i % 2 == 0:
                new_list.append(device_names[i - 1])
        return new_list

    def start_recording(self):
        main_microphone = self.get_main_microphone()
        ffmpeg_devices = self.get_ffmpeg_devices()
        for device in ffmpeg_devices:
            if fuzz.ratio(main_microphone, device) > 80:
                record_microphone = device

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H-%M-%S")
        ffmpeg_path = self.get_ffmpeg_path()
        file_output_name = f"{self.name} {formatted_datetime}.mp4"  
        command = [ffmpeg_path, "-f", "gdigrab", "-framerate", "60", 
        "-i", "desktop", "-f", "dshow", "-i", f"audio={record_microphone}",
        "-c:v" , "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-loglevel", "quiet", file_output_name] 

        print("Recording screen. Press ctrl + c to stop recording")
        try:
            self.recording_process = subprocess.run(command)
        except:
            print("The recording was stopped")
