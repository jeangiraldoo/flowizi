from core.database import database, validations, app_validation


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
    result = validations.add_environment(env_name)
    if not result:
        parser.error("The environment specified already exists")
    else:
        print(f"The {env_name} environment has been added!")


def add_website(parser, env_name, url):
    env_id = database.get_environment_ID(env_name)
    if not env_id and parser:
        parser.error("The environment specified does not exist")

    result = validations.add_website_validation(env_name, url)

    if not result[0] and result[1] == "invalid_url":
        parser.error("The URL is not valid")
    elif not result[0] and result[1] == "insertion_attempt":
        error_message = (
                "There is already a website with that URL"
                f" in the {env_name} environment"
                )
        parser.error(error_message)
    else:
        print(f"The website was successfully added to the {env_name} environment!")


def add_file(parser, env_name, url):
    env_id = database.get_environment_ID(env_name)
    if not env_id and parser:
        parser.error("The environment specified does not exist")

    result = validations.add_file_validation(env_name, url)

    if not result[0] and result[1] == "file not found":
        parser.error(
            "There's no file in your system associated"
            " with the path you typed"
        )
    elif not result[0] and result[1] == "insertion_attempt":
        parser.error(
                "There is already file with that path"
                f" in the {env_name} environment"
                )
    else:
        print(f"The file was successfully added to the {env_name} environment!")


def add_application(parser, env_name):
    if not database.get_environment_ID(env_name):
        parser.error("The environment specified does not exist")

    apps = app_validation.get_installed_apps()
    app_validation.display_apps(apps)
    input_app_name = app_validation.ask_app_name()
    similar_apps = app_validation.get_similar_apps(input_app_name, apps)
    result = app_validation.add_similar_apps(env_name, similar_apps, apps)

    if not result[0] and result[1] == "insertion attempt":
        parser.error(f"The chosen application is already in the {env_name} environment")
    elif not result[0] and result[1] == "empty":
        parser.error(f"There is no app with a name similar to {input_app_name}")
    elif not result[0] and result[1] == "number range":
        parser.error("The number is out of bounds")
    else:
        print(f"The application was successfully added to the {env_name} environment!")
