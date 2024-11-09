from core.database import app_validation
from core.database.validations import Validations, ResultType


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
    result = Validations.add_elem_validation(env_name, "websites", url)

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
    result = Validations.add_elem_validation(env_name, "files", url)

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


def add_application(parser, env_name):
    apps = app_validation.get_installed_apps()
    app_validation.display_apps(apps)
    input_app_name = app_validation.ask_app_name()
    similar_names = app_validation.get_similar_names(input_app_name, apps)
    result = app_validation.start_app_addition(env_name, similar_names, apps)

    if result == ResultType.ENV_NOT_EXISTS:
        parser.error("The environment specified does not exist")
    if result == ResultType.UNSUCCESSFUL_OPERATION:
        parser.error(f"The chosen application is already in the {env_name} environment")
    elif result == ResultType.APP_NOT_EXISTS:
        parser.error(f"There is no app with a name similar to {input_app_name}")
    elif result == ResultType.NO_EXECUTABLES:
        parser.error("There are no executable files in the installation directory for this app")
    elif result == ResultType.INVALID_NUMBER:
        parser.error("The number is out of bounds")
    else:
        print(f"The application was successfully added to the {env_name} environment!")
