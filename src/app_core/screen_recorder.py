import os
import sounddevice
from fuzzywuzzy import fuzz
from datetime import datetime
import subprocess
import re


class ScreenRecorder:
    @staticmethod
    def get_stereo_mix():
        """Returns the name of the stereo mix device if it is available.
        Returns 'false' if it isn't"""
        devices = sounddevice.query_devices()
        for device in devices:
            if "Stereo Mix" in device["name"] or "Mezcla estéreo" in device["name"]:
                for i in ScreenRecorder.get_ffmpeg_devices():
                    if fuzz.ratio(device["name"], i) > 70:
                        return i
        return "false"

    @staticmethod
    def get_ffmpeg_path() -> str:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path = os.path.join(package_dir, '..', "..", 'bin', 'ffmpeg_windows.exe')
        return ffmpeg_path

    @staticmethod
    def get_main_microphone():
        main_mic_index = sounddevice.default.device[0]
        devices = sounddevice.query_devices()
        main_mic = devices[main_mic_index]["name"]
        return main_mic

    @staticmethod
    def get_ffmpeg_devices():
        """Returns the devices FFmpeg can detect in the computer.
        FFmpeg expectes to use one of these devices to record audio"""

        command = (
            f"{ScreenRecorder.get_ffmpeg_path()} -list_devices true -f dshow -i dummy"
        )

        command_process = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding = "utf-8")
        device_names = re.findall(r'"([^"]+)" \((audio)\)', command_process.stderr)
        audio_devices = [device[0] for device in device_names]  # Get the first element from each tuple

        return audio_devices

    @staticmethod
    def start_recording(name):
        flowizi_recording_dir = "C:/Users/jeanp/Videos/flowizi"
        environment_recording_dir = f"{flowizi_recording_dir}/{name}"
        main_microphone = ScreenRecorder.get_main_microphone()
        stereo = ScreenRecorder.get_stereo_mix()
        ffmpeg_devices = ScreenRecorder.get_ffmpeg_devices()
        ffmpeg_path = ScreenRecorder.get_ffmpeg_path()

        current_datetime = datetime.now()
        formatted_datetime = current_datetime.strftime("%d-%m-%Y %H_%M_%S")

        video_output_name = f"video_{formatted_datetime}.mp4"
        audio_output_name = f"audio_{formatted_datetime}.mp3"
        merge_output_name = f"{formatted_datetime}.mp4"

        if not os.path.isdir(flowizi_recording_dir):
            os.makedirs(flowizi_recording_dir)
        if not os.path.isdir(environment_recording_dir):
            os.makedirs(environment_recording_dir)

        video_command = [
            ffmpeg_path, "-f", "gdigrab", "-framerate", "60",
            "-i", "desktop", "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", "-loglevel", "quiet",
            f"{environment_recording_dir}/{video_output_name}"
        ]

        if len(ffmpeg_devices) > 0:
            record_microphone = ""
            for device in ffmpeg_devices:
                if fuzz.ratio(main_microphone, device) > 80:
                    record_microphone = device
                    break

            video_command.insert(7, "-f")
            video_command.insert(8, "dshow")
            video_command.insert(9, "-i")
            video_command.insert(10, f"audio={record_microphone}")

        system_audio_command = [
            ffmpeg_path, "-f", "dshow", "-i", f"audio={stereo}", "-c:a",
            "libmp3lame", "-b:a", "192k", "-y", "-loglevel", "quiet",
            f"{environment_recording_dir}/{audio_output_name}"
        ]

        merge_command = [
            ffmpeg_path,
            "-i", f"{environment_recording_dir}/{video_output_name}",
            "-i", f"{environment_recording_dir}/{audio_output_name}",
            "-filter_complex",              # Define the filter graph
            "[0:a]volume=3[v0];[1:a]volume=2.5[a1];[v0][a1]amix=inputs=2:duration=longest[a];",  # Mix audio with adjusted volumes
            "-map", "0:v",                  # Map video stream from the first input
            "-map", "[a]",                  # Map the mixed audio stream
            "-c:v", "copy",                 # Copy video stream
            "-c:a", "aac",                  # Set audio codec to AAC
            "-b:a", "192k",                 # Set audio bitrate (optional)
            "-loglevel", "quiet",
            "-strict", "experimental",      # Use experimental AAC encoder if needed
            f"{environment_recording_dir}/{merge_output_name}"
        ]

        if stereo == "false":
            print((
                "The Stereo mix setting is not enabled. The screen and "
                "microphone audio will be recorded but the system audio "
                "will not.\nRecording screen. Press Ctrl + c to stop recording"
                ))
            try:
                subprocess.run(video_command)
            except:
                print("The recording was stopped")
        else:
            print("Recording screen. Press ctrl + c to stop recording")
            system_audio_process = subprocess.Popen(system_audio_command)
            try:
                subprocess.run(video_command)
            except:
                system_audio_process.terminate()
                merge_process = subprocess.Popen(merge_command)
                print("The recording was stopped")
                while merge_process.poll() == None:
                    continue
                os.remove(f"{environment_recording_dir}/{video_output_name}")
                os.remove(f"{environment_recording_dir}/{audio_output_name}")
