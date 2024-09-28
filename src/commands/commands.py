import os
import platform
from src.bootstrap import setup
from urllib.parse import urlparse
from src.app_core.flowizi import flowizi
from src.app_core.website import Website
from src.app_core.environment import Environment

def handle_arguments(args):
    """Process optional flags used when running flowizi"""
    if args.v:
        print(f"Flowizi {flowizi.version}")


def start(args, parser):
    name_exists = any(environment.name == args.name for environment in flowizi.environment_list)
    if not name_exists:
        parser.error("The environment specified does not exist")
    for environment in flowizi.environment_list:
        if environment.name == args.name:
            environment.start()
            break


def remove(args, parser):
    """Remove a link from the configuration file"""
    found = flowizi.exists_environment_list(args.name)
    if not(found):
        parser.error("There's no environment with that name")

    if args.w != "false":
        attribute = "websites"
        value = args.w

        exists = flowizi.exists_environment_element(args.name, attribute, value)
        if not exists:
            parser.error("The element specfified does not exist")
        flowizi.remove_environment_element(args.name, attribute, value) 
    else:
        flowizi.remove_environment(args.name)

def show_system_info(args):
    print(f"Operating system: {flowizi.os_name}\nUser: {flowizi.user}")


def list_(args):
    if len(flowizi.environment_list) == 0:
        print("There's no environments. You can add one by using the add command, followed by the environment name")
    else:
        print("Environment list:")
        for i in flowizi.environment_list:
            print(f"{i.name}")


def add(args, parser):
    if args.w != "false":
        website_name, website_link = args.w
        name_exists = any(environment.name == args.name for environment in flowizi.environment_list)
        if not name_exists:
            parser.error("The environment specified does not exist")
        if not flowizi.verify_URL(website_link):
            parser.error("The link does not follow a proper link format")

        for environment in flowizi.environment_list:
            website_exists = any(website.name == website_name for website in environment.websites)
            if environment.name == args.name and len(environment.websites) > 0 and website_exists:
                parser.error("This website already exists")

        new_website = Website(website_name, website_link)
        flowizi.add_environment_element(args.name, "websites", new_website)
        print(f"The {website_name} website was added to the {args.name} environment")
    else:
        #Validates if the name is already in the json file
        used_name = any(environment.name == args.name for environment in flowizi.environment_list)
        if used_name:
            parser.error("The environment name has been added in the past")

        environment = Environment(args.name)
        flowizi.add_environment(environment)
        print(f"The {args.name} environment has been added!")
