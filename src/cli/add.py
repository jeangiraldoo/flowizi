from core.system_detection import application_detection
from core.database.validations import Validations, ResultType
from core.elements.element import ElementType
from cli._utils import display_items, get_pos


def add_command(args, parser):
    if args.w:
        website_url = args.w[0]
        add_website(parser, args.name, website_url)
    elif args.f:
        file_url = args.f[0]
        add_file(parser, args.name, file_url)
    elif args.a:
        add_application(parser, args.name)
    else:
        add_environment(parser, args.name)


def add_environment(parser, env_name):
    '''Calls the function that inserts environments into the database

    Parameters:
    parser ("" or ArgumentParser): Defines how the feedback will be shown (CLI/GUI)
    env_name (Str): Name of the environment to add'''
    result = Validations.add_env_validation(env_name)
    if not result:
        parser.error("The environment specified already exists")

    print(f"The {env_name} environment has been added!")


def add_website(parser, env_name, url):
    result = Validations.add_elem_validation(env_name, ElementType.WEBSITE, url)

    if result == ResultType.INVALID_URL:
        parser.error("The URL is not valid")
    elif result == ResultType.ENV_NOT_EXISTS:
        parser.error("The environment specified does not exist")
    elif result == ResultType.UNSUCCESSFUL_OPERATION:
        error_message = (
                "There is already a website with that URL"
                f" in the {env_name} environment"
                )
        parser.error(error_message)
    else:
        print(f"The website was successfully added to the {env_name} environment!")


def add_file(parser, env_name, url):
    result = Validations.add_elem_validation(env_name, ElementType.FILE, url)

    if result == ResultType.ENV_NOT_EXISTS:
        parser.error("The environment specified does not exist")
    elif result == ResultType.INVALID_URL:
        parser.error(
            "There's no file in your system associated"
            " with the path you typed"
        )
    elif result == ResultType.UNSUCCESSFUL_OPERATION:
        parser.error(
                "There is already file with that path"
                f" in the {env_name} environment"
                )
    else:
        print(f"The file was successfully added to the {env_name} environment!")


def add_application(parser, env_name: str):
    apps = application_detection.get_apps()
    display_items(ElementType.APP.value, apps, "no index")
    input_name = input("\nType the name/part of the name of any app: ")
    similar_names = application_detection.get_similar_names(input_name, apps)

    if len(similar_names) == 0:
        parser.error(f"There is no app with a name similar to {input_name}")
    elif len(similar_names) == 1:
        add_one_similar_app(parser, env_name, similar_names[0], apps)
    else:
        result = add_multiple_similar_apps(parser, env_name, apps, similar_names)
        show_feedback(parser, env_name, result)


def choose_exe(parser, env_name: str, execs, exe_name: str, exe_path: str):
    confirmation = request_exe_confirmation(exe_name)
    if confirmation:
        result = Validations.add_elem_validation(env_name, ElementType.APP, exe_path)
    else:
        exe_path = manually_choose_exe(execs)
        result = Validations.add_elem_validation(env_name, ElementType.APP, exe_path)

    return result


def add_one_similar_app(parser, env_name, app_name, apps):
    execs = application_detection.get_execs(apps[app_name])
    if len(execs) == 0:
        msg = ("There are no executable files in the detected directory:"
               f"\n{apps[app_name]}\n\n"
               "If this is not the correct installation directory, you can go to"
               " the correct directory and add the executable file as a file"
               " instead of an application."
               )
        parser.error(msg)
    else:
        exe_name, exe_path = application_detection.detect_exe(app_name, execs)
        result = choose_exe(parser, env_name, execs, exe_name, exe_path)
        show_feedback(parser, env_name, result)


def add_multiple_similar_apps(parser, env_name: str, apps: dict, similar_names: list) -> ResultType:
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
        ResultType: Enum that indicates the result of the operation.
    """
    display_items(ElementType.APP.value, similar_names, "index")
    pos = get_pos(1, len(similar_names))

    if pos == ResultType.INVALID_NUMBER:
        return ResultType.INVALID_NUMBER

    app_name = similar_names[pos - 1]
    app_path = apps[app_name]
    exec_files = application_detection.get_execs(app_path)

    if len(exec_files) == 0:
        return ResultType.NO_EXECUTABLES

    exe_name, path = application_detection.detect_exe(app_name, exec_files)
    answer = request_exe_confirmation(exe_name)
    if answer:
        result = Validations.add_elem_validation(env_name, "applications", path)
    else:
        result = reject_detected_exec(env_name, app_name, exec_files)

    return result


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
        ResultType: Enum that indicates the result of the operation.
    """
    exe_result = manually_choose_exe(exec_files)
    if exe_result == ResultType.INVALID_NUMBER:
        return ResultType.INVALID_NUMBER
    return Validations.add_elem_validation(env_name, ElementType.APP, exe_result)


def show_feedback(parser, env_name, result: ResultType):
    """Displays feedback to the user based on the ResultType from validation.

    Args:
        parser: Parser object used to create error messages.
        env_name (str): Name of the environment.
        result (ResultType): Result type obtained.
    """

    if result == ResultType.ENV_NOT_EXISTS:
        parser.error("The environment specified does not exist")
    elif result == ResultType.UNSUCCESSFUL_OPERATION:
        parser.error(f"The chosen application is already in the {env_name} environment")
    elif result == ResultType.NO_EXECUTABLES:
        parser.error("There are no executable files in the installation directory for this app")
    elif result == ResultType.INVALID_NUMBER:
        parser.error("The number is out of bounds")
    else:
        print(f"The application was successfully added to the {env_name} environment!")


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
        ResultType: Enum that indicates the result of the operation.
    """
    display_items("executables", final_list, "index")

    pos = get_pos(1, len(final_list))

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
