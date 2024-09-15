import os
import platform
from config import config_manager
from urllib.parse import urlparse
from app_data import lazyMeetings

def handle_arguments(args):
    """Process optional flags used when running lazyMeetings"""
    if(args.v):
        print(f"EasyConfig {lazyMeetings.version}")

def remove(args, parser):
    """Remove a link from the configuration file"""

    if(args.p and args.software_name == "false"):
        parser.error("The path and the software name were not specified")
    elif(args.p and args.software_name == "false"):
        parser.error("The software name was not specified")

    lazyMeetings.parser.read(lazyMeetings.config_path)
    if(not(args.software_name in lazyMeetings.parser["Meetings"])):
        parser.error("There's no app in the paths with that name")
    else:
        config_manager.remove_path_value(args.software_name)

def show_system_info(args):
    print(f"Operating system: {lazyMeetings.os_name}\nUser: {lazyMeetings.user}")

def list_(args):
    lazyMeetings.parser.read(lazyMeetings.config_path)
    if(len(lazyMeetings.parser["Meetings"]) == 0):
        print("There's no links in the configuration file. \nUse the 'add' command with the '-p' flag to add one")
    else:
        print("List of meetings:")
        for key in lazyMeetings.parser["Meetings"]:
            print(f"{key} -> {lazyMeetings.parser['Meetings'][key]}")

def add(args, parser):
    """Add a software_name/path pair to the "Meetings" setting in the configuration file"""
    if(args.p and args.name == "false"):
        parser.error("The name of the software was not provided")
    if(args.p and args.link == "false"):
        parser.error("The path was not provided")

    parsed_link = urlparse(args.link)
    # This checks that the URL has both a scheme (e.g., http or https) and a network location (e.g., example.com)
    if(not(all([parsed_link.scheme, parsed_link.netloc]))):
        parser.error("The link does not follow a proper link format")
        
    #Validates if the name or link is already in the config file
    lazyMeetings.parser.read(lazyMeetings.config_path)
    if(args.name in lazyMeetings.parser["Meetings"]):
        parser.error("The app name has been added in the past")
    else:
        for key in lazyMeetings.parser["Meetings"]:
            if(lazyMeetings.parser["Meetings"][key] == args.path_name):
                parser.error("The path name has been added in the past")
    config_manager.add_path_value(args.name, args.link)
