import winreg
import os
from core.database import database


def get_installed_apps():
    # Define registry paths to check for both machine-wide and user-wide installations
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"  # For 32-bit apps on 64-bit Windows
    ]

    installed_apps = {}
    for path in registry_paths:
        installed_apps.update(get_apps_hive(path, winreg.HKEY_LOCAL_MACHINE))
        installed_apps.update(get_apps_hive(path, winreg.HKEY_CURRENT_USER))

    return installed_apps


def get_apps_hive(registry_path, hive):
    app_dict = {}

    try:
        reg = winreg.ConnectRegistry(None, hive)
        key = winreg.OpenKey(reg, registry_path)
    except FileNotFoundError:
        return app_dict

    try:
        i = 0
        while True:
            subkey_name = winreg.EnumKey(key, i)
            subkey = winreg.OpenKey(key, subkey_name)
            try:
                app_name, _ = winreg.QueryValueEx(subkey, "DisplayName")
                app_path, _ = winreg.QueryValueEx(subkey, "InstallLocation")
                if app_name and app_path:
                    app_dict[app_name] = app_path
            except EnvironmentError:
                pass  # Skip if values don't exist in the subkey
            i += 1
    except WindowsError:
        pass  # End of registry reached

    return app_dict


def display_apps(app_dict):
    if not app_dict:
        print("No installed applications found.")
        return

    print("Detected Applications:\n")
    for app_name in app_dict:
        print(app_name)


def display_items(similar_apps, message):
    print(message)
    for idx, name in enumerate(similar_apps, start = 1):
        print(f"{idx}. {name}")


def ask_app_name():
    input_name = input("\nType the name/part of the name of any app: ")
    return input_name


def ask_pos():
    try:
        choice = int(input("\nChoose one: "))
        return choice
    except:
        print("You must type a number")
        exit(1)


def get_similar_apps(choice, apps):
    similar_apps = []
    for inx, app_name in enumerate(apps):
        if choice in app_name:
            similar_apps.append(app_name)
    return similar_apps


def add_similar_apps(env_name, similar_apps, apps):
    print(similar_apps)
    if len(similar_apps) == 0:
        final_result = [False, "empty"]
    elif len(similar_apps) == 1:
        name = similar_apps[0]
        path = apps[name]
        exec_files = get_exec_files(path)
        exe_path = get_exe_path(exec_files)
        if exe_path is None:
            return [False, "number range"]

        print(exe_path)
        result = add_one_similar_app(env_name, name, exe_path)
        final_result = [result, "insertion attempt"]
    else:
        final_result = add_multiple_similar_apps(env_name, apps, similar_apps)

    return final_result


def add_one_similar_app(env_name, name, path):
    if not database.insert_element(env_name, "applications", name, path):
        return False
    return True


def add_multiple_similar_apps(env_name, apps, similar_apps):
    display_items(similar_apps, "\nThere's multiple apps with that name:")
    pos = ask_pos()

    if not validate_number_range(pos, 1, len(similar_apps)):
        return [False, "number range"]

    app_name = similar_apps[pos - 1]

    app_dir = apps[app_name]
    exec_files: dict = get_exec_files(app_dir)
    exe_path = get_exe_path(exec_files)

    if exe_path is None:
        return [False, "number range"]

    result = database.insert_element(env_name, "applications", app_name, exe_path)
    return [result, "insertion attempt"]


def get_exec_files(app_path) -> dict:
    final_list = {}
    file_list = os.listdir(app_path)
    exec_list = {file: os.path.join(app_path, file) for file in file_list if file[len(file) - 4:] == ".exe"}
    final_list.update(exec_list)

    if os.path.exists(f"{app_path}/bin"):
        bin_list = os.listdir(os.path.join(app_path, "bin"))
        bin_exec_list = {f"bin/{file}": os.path.join(app_path, f"bin/{file}") for file in bin_list if file[len(file) - 4:] == ".exe"}
        final_list.update(bin_exec_list)

    return final_list


def get_exe_path(final_list: dict) -> str:
    display_items(final_list, "\nExecutable files found: ")

    pos = ask_pos()

    for idx, file in enumerate(final_list):
        if idx == pos - 1:
            return final_list[file]


def validate_number_range(number, lower_range, upper_range):
    if number < lower_range or number > upper_range:
        return False
    return True
