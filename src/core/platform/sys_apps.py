import os
import winreg
from winreg import HKEYType
from fuzzywuzzy import fuzz


def get_apps() -> dict[str, str]:
    """Retrieves a list of installed applications from the Windows registry.

    This function searches both the machine-wide and user-specific registry
    paths to find installed applications on the system.

    Returns:
        dict: A dictionary with application names as keys and their
        installation paths as values.
    """
    # Define registry paths to check for both machine-wide and user-wide installations
    registry_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"  # For 32-bit apps on 64-bit Windows
    ]

    installed_apps = {}
    for path in registry_paths:
        installed_apps.update(get_hive_apps(path, winreg.HKEY_LOCAL_MACHINE))
        installed_apps.update(get_hive_apps(path, winreg.HKEY_CURRENT_USER))

    return installed_apps


def get_hive_apps(registry_path: str, hive: HKEYType) -> dict[str, str]:
    """Retrieves applications from a specific Windows registry hive and path.

    Connects to the specified registry hive and path, then attempts to extract
    the name and installation path of each application found. Skips entries
    where these values are missing.

    Args:
        registry_path (str): The path in the registry to search
        for applications.
        hive (HKEYType): The registry hive to access (e.g., HKEY_LOCAL_MACHINE
        or HKEY_CURRENT_USER).

    Returns:
        dict: A dictionary containing application names as keys and their
        installation paths as values.
    """
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


def get_execs(path: str) -> dict[str, str]:
    """Finds all executable files in the root and "bin" directories of a given
    path.

    Args:
        path (str): The directory path to search.

    Returns:
        dict[str, str]: A dictionary mapping each executable's name to its
        full path.
    """
    final_list = {}
    file_list = os.listdir(path)
    exec_list = {file: os.path.join(path, file) for file in file_list if file[len(file) - 4:] == ".exe"}
    final_list.update(exec_list)

    if os.path.exists(f"{path}/bin"):
        bin_list = os.listdir(os.path.join(path, "bin"))
        bin_exec_list = {file: os.path.join(path, f"bin/{file}") for file in bin_list if file[len(file) - 4:] == ".exe"}
        final_list.update(bin_exec_list)

    return final_list


def get_similar_names(name: str, apps: dict) -> list[str]:
    """Returns a list with the app names that are similar to the one given by
    the user.

    Args:
    name (str): Name given by the user.
    apps (dict): A dictionary where the keys are application names and
        the values are the respective directories for those apps.
    """
    similar_names = []
    for inx, app_name in enumerate(apps):
        if name in app_name:
            similar_names.append(app_name)
    return similar_names


def detect_exe(app_name: str, exe_list: dict[str, str]) -> list[str, str]:
    """Matches the app name with the most similar executable file name
    using fuzzy logic, assuming this will often be the main executable.

    Args:
        app_name (str): Name of the application to match.
        exe_list (Dict[str, str]): Dictionary of executable names as keys and
        their paths as values.

    Returns:
        list[str, str]: Name and path to the executable file that most closely
        matches the app name.
    """
    app_name = app_name.lower()
    ratios = []
    exe_names = []
    for exe_name in exe_list:
        ratio = fuzz.partial_ratio(app_name, exe_name.lower())
        ratios.append(ratio)
        exe_names.append(exe_name)

    pos = ratios.index(max(ratios))
    exe_name = exe_names[pos]
    path = exe_list[exe_name]

    return [exe_name, path]


