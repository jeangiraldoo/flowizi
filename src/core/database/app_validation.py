import winreg
import os
from winreg import HKEYType
from fuzzywuzzy import fuzz
from core.database import database
from core.database.validations import ResultType


def get_installed_apps() -> dict[str, str]:
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


def display_apps(app_dict: dict):
    """Lists items from a dictionary.

    Args:
        app_dict dict[str, str]): A dictionary in which the keys
        are application names to be displayed.
    """
    if not app_dict:
        print("No installed applications found.")
        return

    print("Detected Applications:\n")
    for app_name in app_dict:
        print(app_name)


def list_items(message: str, similar_apps: list[str]):
    """Lists items from a list with indexes.

    Args:
        message (str): The message to be displayed before listing the items.
        similar_apps (list[str]): A list of application names to be displayed
        with their indexes.
    """
    print(message)
    for idx, name in enumerate(similar_apps, start = 1):
        print(f"{idx}. {name}")


def ask_app_name() -> str:
    """Prompts the user to input the name of an app from the options shown
    on the screen.

    This function is only called when using the CLI.

    Returns:
        str: The user's choice as a non-empty string.
    """
    input_name = input("\nType the name/part of the name of any app: ")
    return input_name


def ask_pos(lower_range: int, upper_range: int) -> ResultType | int:
    """Prompts the user to input a number that matches one of the items being
    shown on the screen.

    This function is only called when using the CLI.

    Returns:
        int: The user's choice as an integer.
    """
    try:
        pos = int(input("\nChoose one: "))
    except:
        print("You must type a number")
        exit(1)

    if pos < lower_range or pos > upper_range:
        return ResultType.INVALID_NUMBER
    return pos


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


def start_app_addition(env_name: str, sim_names: list[str], apps: dict) -> ResultType:
    """
    Initiates the process of adding an app to the database, selecting the
    appropriate handling method based on the number of similar applications.

    This function evaluates the list of similar app names:
    - If there are no similar names, it returns a failure result indicating
    no apps found.
    - If there is exactly one similar name, it proceeds to add the app using
    the "add_similar_app" function.
    - If there are many similar names, it calls "add_multiple_similar_apps".

    Args:
        env_name (str): The environment name to which the app should be added.
        sim_names (list[str]): A list of app names that are similar to the
        target app name.
        apps (dict): A dictionary of app names as keys and their corresponding
        paths as values.

    Returns:
        list[bool, str]: A list where the first element is a boolean indicating
        success (True) or failure (False), and the second element is a string
        message providing additional information on the operation result:
         - "no app" if no similar apps are found,
         - "insertion attempt" if adding an app was attempted,
         - or other relevant status messages as returned by "add_similar_app"
           or "add_multiple_similar_apps".
    """
    if len(sim_names) == 0:
        result = ResultType.APP_NOT_EXISTS
    elif len(sim_names) == 1:
        result = add_similar_app(env_name, sim_names[0], apps, "CLI")
    else:
        result = add_multiple_similar_apps(env_name, apps, sim_names)

    return result


def add_similar_app(env_name: str, name: str, apps: dict, interface: str) -> list[bool, str]:
    """
    Attempts to add an app to the database when there is a single app installed
    on the system with a name similar to the one provided by the user.

    This function is typically used by the GUI, where the exact name of the
    application is provided by clicking a label named after the app.

    It can also be used by the CLI if there is only a single app with a similar
    name to the one given by the user.

    Args:
        env_name (str): The name of the environment the app should be added to.
        name (str): The name of the application (exact match from the "apps"
        dictionary).
        apps (dict): A dictionary where the keys are application names and
        the values are the respective directories for those apps.

    Returns:
        list: A list containing a boolean indicating success or failure, and a
        status message. The status message can indicate the result of
        the operation, such as "empty" when there are 0 executable files in the
        directory, or "insertion attempt" when there are executable files and
        an attempt to add an entry to the database was made.
    """
    app_path = apps[name]
    exec_files = get_all_execs(app_path)

    if len(exec_files) == 0:
        return ResultType.NO_EXECUTABLES

    if interface == "CLI":
        exe_name, path = get_final_path(name, exec_files)
        answer = request_exe_confirmation(exe_name)
        if answer:
            return accept_detected_exec(env_name, name, path)
        else:
            return reject_detected_exec(env_name, name, exec_files)

    path = get_final_path(name, exec_files)[1]
    return finish_add_app(env_name, name, path)


def add_multiple_similar_apps(env_name: str, apps: dict, similar_names: list) -> list[bool, str]:
    """
    Attempts to add an app to the database when there are many apps installed
    on the system with a name similar to the one provided by the user.

    This function is only used by the CLI, where multiple applications
    may have names similar to the one provided by the user.

    The GUI on the other hand, uses an exact match for an app.

    Args:
        env_name (str): The name of the environment the app should be added to.
        apps (dict): A dictionary where the keys are application names and the
        values are the respective directories for those apps.
        similar_apps (list): A list of application names that are similar to
        the name provided by the user.

    Returns:
        list: A list containing a boolean indicating success or failure, and a
        status message. If the user selects an invalid number or the app cannot
        be added, the function returns a failure message.
    """
    list_items("\nThere's multiple apps with that name:", similar_names)
    pos = ask_pos(1, len(similar_names))

    if pos == ResultType.INVALID_NUMBER:
        return pos

    app_name = similar_names[pos - 1]
    app_path = apps[app_name]
    exec_files = get_all_execs(app_path)

    if len(exec_files) == 0:
        return ResultType.NO_EXECUTABLES

    exe_name, path = get_final_path(app_name, exec_files)
    answer = request_exe_confirmation(exe_name)
    if answer:
        return accept_detected_exec(env_name, app_name, path)
    else:
        return reject_detected_exec(env_name, app_name, exec_files)


def accept_detected_exec(env_name: str, app_name: str, path: str) -> ResultType:
    """Attempts to add a detected executable file to the specified environment.

    This function is only used by the CLI.

    Args:
        env_name (str): The name of the environment where the app is being
            added.
        app_name (str): The name of the application being added.
        path (str): The path to the executable file.

    Returns:
        list[bool, str]: A list where the first element is a boolean indicating
        whether the insertion was successful, and the second element is a
        message describing the operation done.
    """
    return finish_add_app(env_name, app_name, path)


def reject_detected_exec(env_name: str, app_name: str, exec_files: dict[str, str]) -> ResultType:
    """Allows the user to manually select an executable file if the detected
    one is not preferred.

    This function provides an option to manually choose an executable file from
    the given "exec_files". If a valid executable is selected, it attempts to
    add this executable to the specified environment by calling
    "finish_add_app".

    This function is only used by the CLI.

    Args:
        env_name (str): The name of the environment.
        app_name (str): The name of the application.
        exec_files (dict[str, str]): A dictionary where keys are executable
            names and values are paths to these executables.

    Returns:
        list[bool, str]: A list where the first element is a boolean indicating whether
             the addition to the environment was successful. The second
             element is a description of the result, either "number range"
             if manual selection failed or "insertion attempt" upon attempting
             to insert.
    """
    exe_result = manually_choose_exe(exec_files)
    if exe_result == ResultType.INVALID_NUMBER:
        return ResultType.INVALID_NUMBER
    return finish_add_app(env_name, app_name, exe_result)


def finish_add_app(env_name: str, name: str, path: str) -> ResultType:
    """Attempts to add a new application entry to the database for a given
    environment.

    Args:
        env_name (str): The name of the environment the application instance
        will be associated with.
        name (str): The name of the application.
        path (str): The path to the application, which will be cleaned before
        insertion.

    Returns:
        bool: True if the application was successfully inserted into the
        database, False if the insertion failed.
    """
    path = clean_url(path)

    if not database.insert_element(env_name, "applications", name, path):
        return ResultType.UNSUCCESSFUL_OPERATION

    return ResultType.SUCCESSFUL_OPERATION


def get_all_execs(path: str) -> dict[str, str]:
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


def get_final_path(app_name: str, exe_list: dict[str, str]) -> list[str, str]:
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


def manually_choose_exe(final_list: dict) -> ResultType | str:
    """Displays a list of executable files found in the app's directory
    and prompts the user to choose one.

    This function shows the executable files as options, asks the user to
    select a position, and returns the path of the chosen executable if
    the input is valid.

    Args:
        final_list (dict): A dictionary where the keys are executable
        file names and the values are their corresponding paths.

    Returns:
        str: The path to the selected executable file.
    """
    list_items("\nExecutable files found: ", final_list)

    pos = ask_pos(1, len(final_list))

    if pos == ResultType.INVALID_NUMBER:
        return pos

    for idx, file in enumerate(final_list):
        if idx == pos - 1:
            return final_list[file]


def request_exe_confirmation(exe_name: str) -> bool:
    """
    Asks the user whether to use the detected executable file or manually
    select another.

    This function prompts the user to confirm the automatically detected
    executable file or to choose a different one.

    It is only used in the CLI; in the GUI, a similar confirmation is provided
    through a graphical interface.

    Args:
        exe_name (str): The name of the detected executable file.

    Returns:
        bool: True if the user confirms the detected executable, False if they
              choose to select a different one manually.
    """
    while True:
        msg = (
          f"This is the detected executable that will open the app: {exe_name}"
          '\nDo you wish to use this one (type "y") or select a different one'
          ' manually (type "n")?'
        )

        value = input(msg)
        if value == "y":
            return True
        elif value == "n":
            return False


def clean_url(url):
    """Converts backslashes to forward slashes in a URL, mainly for
    compatibility with Windows file paths."""
    url = url.replace("\\", "/")
    return url
