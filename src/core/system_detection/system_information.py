import platform
import os
from ctypes import windll, byref, c_wchar_p
from uuid import UUID
from pathlib import Path

operating_system = platform.system()
user = os.getlogin()

VIDEOS_ID = UUID("18989b1d-99b5-455b-841c-ab7c74e4ddfc").bytes_le
APPDATA_LOCAL = UUID("F1B32785-6FBA-4FCF-9D55-7B8E7F157091").bytes_le


def get_known_folder_path(folder_id):
    path_ptr = c_wchar_p()
    result = windll.shell32.SHGetKnownFolderPath(folder_id, 0, None, byref(path_ptr))
    if result != 0:
        raise OSError(f"Failed to retrieve folder path, error code: {result}")
    return Path(path_ptr.value)


json_dir = f"{get_known_folder_path(APPDATA_LOCAL)}/flowizi"
json_path = f"{json_dir}/data.json"
record_dir = f"{get_known_folder_path(VIDEOS_ID)}/flowizi"
system_sound_names = ["Stereo Mix", "Stereo-Mix", "Mezcla estéreo",
                      "Mixagem estéreo", "Mixage stéréo", "Mix Stereo",
                      "立体声混音", "ステレオミックス", "스테레오 믹스",
                      "Стерео Микс"]
