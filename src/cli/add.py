from core.platform import sys_apps
from core.text_res.feedback import Feedback
from core.database.validations import Validations, ResultType
from core.elements.element import ElementType
from cli.common.app_io import display_items, get_pos


def add_command(args, parser):
    if args.w:
        elem_type = ElementType.WEBSITE
        url = args.w[0]
        result = Validations.add_elem_validation(args.name, ElementType.WEBSITE, url)
    elif args.f:
        elem_type = ElementType.FILE
        url = args.f[0]
        result = Validations.add_elem_validation(args.name, ElementType.FILE, url)
    elif args.a:
        elem_type = ElementType.APP
        result = add_application(parser, args.name)
    else:
        elem_type = ElementType.ENV
        result = Validations.add_env_validation(args.name)

    show_feedback(parser, args.name, elem_type, result)


def add_application(parser, env_name: str):
    apps = sys_apps.get_apps()
    display_items(ElementType.APP.value, apps, "no index")
    input_name = input("\nType the name/part of the name of any app: ")
    similar_names = sys_apps.get_similar_names(input_name, apps)

    if len(similar_names) == 0:
        result = Feedback.NO_SIMILAR_APP_NAME
    elif len(similar_names) == 1:
        result = add_one_similar_app(parser, env_name, similar_names[0], apps)
    else:
        result = add_multiple_similar_apps(parser, env_name, apps, similar_names)

    return result


def add_one_similar_app(parser, env_name: str, app_name: str, apps):
    execs = sys_apps.get_execs(apps[app_name])
    if len(execs) == 0:
        msg = ("There are no executable files in the detected directory:"
               f"\n{apps[app_name]}\n\n"
               "If this is not the correct installation directory, you can go to"
               " the correct directory and add the executable file as a file"
               " instead of an application."
               )
        parser.error(msg)
    else:
        exe_name, exe_path = sys_apps.detect_exe(app_name, execs)
        return choose_exe(parser, env_name, execs, exe_name, exe_path)


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
    exec_files = sys_apps.get_execs(app_path)

    if len(exec_files) == 0:
        msg = ("There are no executable files in the detected directory:"
               f"\n{apps[app_name]}\n\n"
               "If this is not the correct installation directory, you can go to"
               " the correct directory and add the executable file as a file"
               " instead of an application."
               )
        parser.error(msg)

    exe_name, path = sys_apps.detect_exe(app_name, exec_files)
    answer = request_exe_confirmation(exe_name)
    if answer:
        result = Validations.add_elem_validation(env_name, "applications", path)
    else:
        exe_result = manually_choose_exe(exec_files)
        if exe_result == ResultType.INVALID_NUMBER:
            result = ResultType.INVALID_NUMBER
        else:
            result = Validations.add_elem_validation(env_name, ElementType.APP, exe_result)

    return result


def choose_exe(parser, env_name: str, execs, exe_name: str, exe_path: str):
    confirmation = request_exe_confirmation(exe_name)
    if confirmation:
        result = Validations.add_elem_validation(env_name, ElementType.APP, exe_path)
    else:
        exe_path = manually_choose_exe(execs)
        result = Validations.add_elem_validation(env_name, ElementType.APP, exe_path)

    return result


def show_feedback(parser, env_name, elem_type, result: ResultType):
    """Displays feedback to the user based on the ResultType from validation.

    Args:
        parser: Parser object used to create error messages.
        env_name (str): Name of the environment.
        result (ResultType): Result type obtained.
    """
    sing_type = elem_type.value[:len(elem_type.value) - 1]  # string without the last 's'

    if result == ResultType.ENV_CREATED:
        print(Feedback.ENVIRONMENT_SUCCESS.value.format(env_name=env_name)) 
    elif result == ResultType.ENV_ALREADY_EXISTS:
        print(Feedback.ENV_ALREADY_EXISTS)
    elif result == ResultType.ENV_NOT_EXISTS:
        parser.error(Feedback.ENV_NOT_EXISTS.value)
    elif result == ResultType.UNSUCCESSFUL_OPERATION:
        parser.error(Feedback.ELEMENT_ALREADY_EXISTS.value.format(elem_type=sing_type, env_name=env_name))
    elif result == ResultType.INVALID_NUMBER:
        parser.error(Feedback.NUMBER_OUT_OF_BOUNDS.value)
    elif result == ResultType.INVALID_URL:
        parser.error(Feedback.WEBSITE_INVALID_URL.value)
    elif result == ResultType.INVALID_FILE_PATH:
        parser.error(Feedback.FILE_NOT_FOUND.value)
    else:
        print(f"The {sing_type} was successfully added to the {env_name} environment!")



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
