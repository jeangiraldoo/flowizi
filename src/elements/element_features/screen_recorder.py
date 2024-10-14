import os
import sounddevice
from fuzzywuzzy import fuzz
from datetime import datetime
import subprocess
import re
from system_detection.system_information import record_dir
from system_detection.system_information import system_sound_names


class ScreenRecorder:
    main_microphone = None
    ffmpeg_devices = None
    ffmpeg_path = None
    stereo = None
    formatted_datetime = datetime.now().strftime("%d-%m-%Y %H_%M_%S")

    video_output_name = f"video_{formatted_datetime}.mp4"
    audio_output_name = f"audio_{formatted_datetime}.mp3"
    merge_output_name = f"{formatted_datetime}.mp4"

    @staticmethod
    def initialize():
        ScreenRecorder.main_microphone = ScreenRecorder.get_main_microphone()
        ScreenRecorder.ffmpeg_path = ScreenRecorder.get_ffmpeg_path()
        ScreenRecorder.ffmpeg_devices = ScreenRecorder.get_ffmpeg_devices()
        ScreenRecorder.stereo = ScreenRecorder.get_stereo_mix()

    @staticmethod
    def get_stereo_mix():
        """Returns the name of the stereo mix device if it is available.
        Returns 'false' if it isn't"""
        devices = sounddevice.query_devices()
        for device in devices:
            if any(name in device["name"] for name in system_sound_names):
                for i in ScreenRecorder.ffmpeg_devices:
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
            f"{ScreenRecorder.ffmpeg_path} -list_devices true -f dshow -i dummy"
        )

        command_process = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True, encoding = "utf-8")
        device_names = re.findall(r'"([^"]+)" \((audio)\)', command_process.stderr)
        audio_devices = [device[0] for device in device_names]  # Get the first element from each tuple

        return audio_devices

    @staticmethod
    def start_recording(name):
        ScreenRecorder.initialize()
        env_rec_dir = f"{record_dir}/{name}"

        os.makedirs(record_dir, exist_ok = True)
        os.makedirs(env_rec_dir, exist_ok = True)

        if ScreenRecorder.stereo == "false":
            print((
                "The Stereo mix setting is not enabled. The screen and "
                "microphone audio will be recorded but the system audio "
                "will not.\nRecording screen. Press Ctrl + c to stop recording"
                ))
            ScreenRecorder.record_video(env_rec_dir)
        else:
            audio_process = ScreenRecorder.record_audio(env_rec_dir)
            ScreenRecorder.record_video(env_rec_dir)
            audio_process.terminate()
            merge_process = ScreenRecorder.merge_files(env_rec_dir)
            while merge_process.poll() is None:
                continue
            os.remove(f"{env_rec_dir}/{ScreenRecorder.video_output_name}")
            os.remove(f"{env_rec_dir}/{ScreenRecorder.audio_output_name}")
            print(f"Processing finished! Your recording is available at: {env_rec_dir}")

    @staticmethod
    def record_video(dir):
        command = [
            ScreenRecorder.ffmpeg_path, "-f", "gdigrab", "-framerate", "60",
            "-i", "desktop", "-c:v", "libx264", "-preset", "ultrafast",
            "-pix_fmt", "yuv420p", "-loglevel", "quiet",
            f"{dir}/{ScreenRecorder.video_output_name}"
        ]

        if len(ScreenRecorder.ffmpeg_devices) > 0:
            record_microphone = ""
            for device in ScreenRecorder.ffmpeg_devices:
                if fuzz.ratio(ScreenRecorder.main_microphone, device) > 80:
                    record_microphone = device
            command.insert(7, "-f")
            command.insert(8, "dshow")
            command.insert(9, "-i")
            command.insert(10, f"audio={record_microphone}")

        print("Recording screen. Press ctrl + c to stop recording")
        try:
            subprocess.run(command)
        except:
            print("The recording was stopped")

    @staticmethod
    def record_audio(dir):
        command = [
            ScreenRecorder.ffmpeg_path, "-f", "dshow", "-i", f"audio={ScreenRecorder.stereo}", "-c:a",
            "libmp3lame", "-b:a", "192k", "-y", "-loglevel", "quiet",
            f"{dir}/{ScreenRecorder.audio_output_name}"
        ]

        return subprocess.Popen(command)

    @staticmethod
    def merge_files(dir):
        command = [
            ScreenRecorder.ffmpeg_path,
            "-i", f"{dir}/{ScreenRecorder.video_output_name}",
            "-i", f"{dir}/{ScreenRecorder.audio_output_name}",
            "-filter_complex",              # Define the filter graph
            "[0:a]volume=3[v0];[1:a]volume=2.5[a1];[v0][a1]amix=inputs=2:duration=longest[a];",  # Mix audio with adjusted volumes
            "-map", "0:v",                  # Map video stream from the first input
            "-map", "[a]",                  # Map the mixed audio stream
            "-c:v", "copy",                 # Copy video stream
            "-c:a", "aac",                  # Set audio codec to AAC
            "-b:a", "192k",                 # Set audio bitrate (optional)
            "-loglevel", "quiet",
            "-strict", "experimental",      # Use experimental AAC encoder if needed
            f"{dir}/{ScreenRecorder.merge_output_name}"
        ]

        print("Processing the recording...")

        return subprocess.Popen(command)
