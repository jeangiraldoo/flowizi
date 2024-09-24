import os
import platform
from src.bootstrap import setup
from urllib.parse import urlparse
from src.app_core.flowizi import flowizi
from src.app_core.meetings import Meeting
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
    if args.name == "false":
        parser.error("The path and the software name were not specified")
    elif args.name == "false":
        parser.error("The software name was not specified")
    found = flowizi.exists_environment_list(args.name)
    if not(found):
        parser.error("There's no Meeting with that name")
    flowizi.remove_environment(args.name)


def show_system_info(args):
    print(f"Operating system: {flowizi.os_name}\nUser: {flowizi.user}")


def list_(args):
    if len(flowizi.environment_list) == 0:
        print("There's no meetings. You can add one by using the add command with the -p flag, followed by the Meeting name and link")
    else:
        print("Environment list:")
        for i in flowizi.environment_list:
            print(f"{i.name}")


def add(args, parser):
    """Add a software_name/path pair to the "Meetings" setting in the configuration file"""
    if args.name == "false":
        parser.error("The name of the software was not provided")
    
    if args.m != "false":
        meeting_name, meeting_link = args.m
        name_exists = any(environment.name == args.name for environment in flowizi.environment_list)
        if not name_exists:
            parser.error("The environment specified does not exist")

        parsed_link = urlparse(meeting_link)
        if not(all([parsed_link.scheme, parsed_link.netloc])):
            parser.error("The link does not follow a proper link format")
        for environment in flowizi.environment_list:
            if environment.name == args.name and len(environment.meetings) > 0:
                    meeting_exists = any(Meeting.name == meeting_name for Meeting in environment.meetings)
                    if meeting_exists:
                        parser.error("The Meeting specified already exists")
        new_meeting = Meeting(meeting_name, meeting_link)
        flowizi.add_environment_element(args.name, "meetings", new_meeting)
        print(f"The {meeting_name} meeting was added to the {args.name} environment")
    elif args.w != "false":
        website_name, website_link = args.w
        name_exists = any(environment.name == args.name for environment in flowizi.environment_list)
        if not name_exists:
            parser.error("The environment specified does not exist")

        parsed_link = urlparse(website_link)
        if not(all([parsed_link.scheme, parsed_link.netloc])):
            parser.error("The link does not follow a proper link format")

        for environment in flowizi.environment_list:
            if environment.name == args.name and len(environment.meetings) > 0:
                website_exists = any(website.name == website_name for website in environment.websites)
                if website_exists:
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
