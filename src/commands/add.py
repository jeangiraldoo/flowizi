import os
import winreg
from src.flowizi import flowizi
from src.element_utils import utils


def add(args, parser):
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
    if flowizi.json.exists_environment(env_name):
        parser.error("The environment specified already exists")

    flowizi.json.add_environment(env_name)
    print(f"The {env_name} environment has been added!")


def add_website(parser, env_name, url):
    if not flowizi.json.exists_environment(env_name):
        parser.error("The environment specified does not exist")

    if not utils.verify_URL(url, "website"):
        url = f"https://{url}"
        if not utils.verify_URL(url, "website"):
            parser.error("The link does not follow a proper link format")

    name = url[url.rfind("/") + 1:]
    for environment in flowizi.environment_list:
        website_exists = any(website.name == name for website in environment.websites)
        if environment.name == env_name and len(environment.websites) > 0 and website_exists:
            parser.error("This website already exists")

    website = create_website(name, url)
    flowizi.json.add_environment_element(env_name, "websites", website)
    print(f"The {name} website was added to the {env_name} environment")


def create_website(name, url):
    return {"name": name, "url": url}


def add_file(parser, env_name, url):
    if not flowizi.json.exists_environment(env_name):
        parser.error("The environment specified does not exist")

    if not utils.verify_URL(url, "file"):
        parser.error(
            "There's no file in your system associated"
            " with the path you typed"
        )

    url = url.replace("\\", "/")
    name = url[url.rfind("/") + 1:]

    for environment in flowizi.environment_list:
        file_exists = any(file.name == name for file in environment.files)
        if environment.name == env_name and len(environment.websites) > 0 and file_exists:
            parser.error("This file already exists")

    file = create_file(name, url)
    flowizi.json.add_environment_element(env_name, "files", file)
    print(f"The {name} in the {url} path was added to the {env_name} environment")


def create_file(name, url):
    return {"name": name, "url": url}


def add_application(parser, env_name):
    if not flowizi.json.exists_environment(env_name):
        parser.error("The environment specified does not exist")

    apps = get_all_installed_apps()
    app_names = list(apps.keys())
    display_apps(apps)
    position, choice, similar_apps = ask_app_name(apps, app_names)

    if len(similar_apps) == 0:
        print(f"There's no app named {choice} or with {choice} as part of its name")
        exit(1)
    elif len(similar_apps) == 1:
        add_one_similar_app(parser, env_name, position, apps, app_names)
    else:
        add_similar_apps(parser, env_name, apps, similar_apps)


def ask_app_name(apps, app_names):
    position = ""
    similar_apps = [] #stores the app names that are similar to the user's choice
    if apps:
        choice = input("\nType the name/part of the name of any app: ")
        for inx, app_name in enumerate(app_names):
            if choice in app_name:
                position = inx
                similar_apps.append(app_name)

    return [position, choice, similar_apps]


def add_one_similar_app(parser, env_name, position, apps, app_names):
    selected_app = app_names[position]

    if flowizi.json.exists_environment_element(env_name, "applications", selected_app):
        parser.error(f"The {selected_app} application already exists in the {env_name} environment")

    app_dir = apps[selected_app]
    path_to_exe = get_exe(parser, app_dir)
    create_app(env_name, selected_app, path_to_exe)


def add_similar_apps(parser, env_name, apps, similar_apps):
    print("\nThere's multiple apps with that name:")
    for idx, name in enumerate(similar_apps, start = 1):
        print(f"{idx}. {name}")

    try:
        choice = int(input("\nChoose one: "))
    except:
        print("You must type a number")
        exit(1)

    try:
        if not validate_number_range(choice, 1, len(similar_apps)):
            raise ValueError("Error. The number you typed is not within the range of the app list")
    except ValueError as e:
        print(e)
        exit(1)

    selected_app = similar_apps[choice - 1]

    if flowizi.json.exists_environment_element(env_name, "applications", selected_app):
        parser.error(f"The {selected_app} application already exists in the {env_name} tenvironment")

    app_dir = apps[selected_app]
    path_to_exe = get_exe(parser, app_dir)
    create_app(env_name, selected_app, path_to_exe)


def get_all_installed_apps():
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


def get_exe(parser, app_path):
    final_list = {}
    file_list = os.listdir(app_path)
    exec_list = {file: os.path.join(app_path, file) for file in file_list if file[len(file) - 4:] == ".exe"}
    final_list.update(exec_list)

    if os.path.exists(f"{app_path}/bin"):
        bin_list = os.listdir(os.path.join(app_path, "bin"))
        bin_exec_list = {f"bin/{file}": os.path.join(app_path, f"bin/{file}") for file in bin_list if file[len(file) - 4:] == ".exe"}
        final_list.update(bin_exec_list)

    print("\nExecutable files found: ")
    for inx, file in enumerate(final_list, start = 1):
        print(f"{inx}. {file}")
    try:
        choice = int(input("\nType the number associated with the file: "))
    except:
        print("You must type a number")

    try:
        if not validate_number_range(choice, 1, len(final_list)):
            raise ValueError("Error. The number you typed is not within the range of the list of executables")
    except ValueError as e:
        print(e)
        exit(1)

    for idx, file in enumerate(final_list):
        if idx == choice - 1:
            return final_list[file]


def create_app(env_name, name, url):
    application = {"name": name, "url": url}
    flowizi.json.add_environment_element(env_name, "applications", application)


def validate_number_range(number, lower_range, upper_range):
    if number < lower_range or number > upper_range:
        return False
    return True
