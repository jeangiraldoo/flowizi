import pyaudio
import os
from datetime import datetime
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
        self.record()
        for meeting in self.meetings:
            meeting.start()
            meeting.record()
        for website in self.websites:
            website.start()

    def get_ffmpeg_path(self) -> str:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(package_dir, '..', "..", 'bin', 'ffmpeg.exe')
        return ffmpeg_path

    def get_microphone_list(self):
        audio = pyaudio.PyAudio()
        microphones = []

        for index in range(audio.get_device_count()):
            device_info = audio.get_device_info_by_index(index)
            if device_info["maxInputChannels"] > 0:
                microphones.append(device_info["name"])
        return microphones

    def record(self):
        microphone_list = self.get_microphone_list()
        print(type(microphone_list[1]))
        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%Y-%m-%d %H-%M-%S")
        ffmpeg_path = self.get_ffmpeg_path()
        microphone_name = microphone_list[1] + "udio)"
        fixed_name = microphone_name.encode('utf-8').decode('utf-8')
        print(fixed_name)
        file_output_name = f"{self.name} {formatted_datetime}.mp4"  
        command = [ffmpeg_path, "-f", "gdigrab", "-framerate", "60", 
        "-i", "desktop", "-f", "dshow", "-i", f"audio=Varios micrófonos (Realtek(R) Audio)", 
        "-c:v" , "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p", "-loglevel", "quiet", file_output_name] 

        print("Recording screen. Press ctrl + c to stop recording")
        try:
            self.recording_process = subprocess.run(command)
        except:
            print("Recording stopped")
