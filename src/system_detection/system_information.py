import platform
import os
import locale

operating_system = platform.system()
user = os.getlogin()

system_locale = locale.getdefaultlocale()

# The language is usually the first element in the tuple
system_language_code = system_locale[0]
language = system_language_code[:2]


def english():
    values = {"json_dir": f"C:/Users/{user}/AppData/Local/flowizi",
              "json": f"C:/Users/{user}/AppData/Local/flowizi/data.json",
              "record_dir": f"C:/Users/{user}/Videos/flowizi"}
    return values


def spanish():
    values = {"json_dir": f"C:/Usuarios/{user}/AppData/Local/flowizi",
              "json": f"C:/Usuarios/{user}/AppData/Local/flowizi/data.json",
              "record_dir": f"C:/Usuarios/{user}/Videos/flowizi"}
    return values


def get_language(language):
    if language == "en":
        return english()
    elif language == "es":
        return spanish()


values = get_language(language)
json_dir = values["json_dir"]
json_path = values["json"]
record_dir = values["record_dir"]
system_sound_names = ["Stereo Mix", "Mezcla estéreo"]
