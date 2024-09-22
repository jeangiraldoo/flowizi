import os
import platform
from src.bootstrap import setup
from urllib.parse import urlparse
from src.app_core.flowizi import flowizi
from src.app_core.environment import Environment

def handle_arguments(args):
    """Process optional flags used when running flowizi"""
    if args.v:
        print(f"Flowizi {flowizi.version}")

def meeting(args, parser):
    if args.time != "false":
        flowizi.update_meeting(args.time[0], "time", args.time[1])

def join(args, parser):
    if args.name == "false":
        parser.error("The meeting name was not specified")

    found = flowizi.exists_meeting_list(args.name)
    if not(found):
        parser.error("There's no meeting with that name")
    flowizi.join_meeting(args.name)


def remove(args, parser):
    """Remove a link from the configuration file"""
    if args.name == "false":
        parser.error("The path and the software name were not specified")
    elif args.name == "false":
        parser.error("The software name was not specified")
    found = flowizi.exists_meeting_list(args.name)
    if not(found):
        parser.error("There's no meeting with that name")
    flowizi.remove_meeting(args.name)


def show_system_info(args):
    print(f"Operating system: {flowizi.os_name}\nUser: {flowizi.user}")


def list_(args):
    if len(flowizi.environment_list) == 0:
        print("There's no meetings. You can add one by using the add command with the -p flag, followed by the meeting name and link")
    else:
        print("Environment list:")
        for i in flowizi.environment_list:
            print(f"{i.name}")


def add(args, parser):
    """Add a software_name/path pair to the "Meetings" setting in the configuration file"""
    if args.name == "false":
        parser.error("The name of the software was not provided")

    #Validates if the name is already in the json file
    for environment in flowizi.environment_list:
        if environment.name == args.name:
            parser.error("The meeting name has been added in the past")

    environment = Environment(args.name)
    flowizi.add_environment(environment)
    print(f"The {args.name} environment has been added!")
