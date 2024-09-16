import os
import platform
import meetings
from config import setup
from urllib.parse import urlparse
from app_data.lazymeetings import lazyMeetings

def handle_arguments(args):
    """Process optional flags used when running lazyMeetings"""
    if(args.v):
        print(f"Lazy Meetings {lazyMeetings.version}")

def join(args, parser):
    if(args.name == "false"):
        parser.error("The meeting name was not specified")

    found = lazyMeetings.exists_meeting_list(args.name)
    if(not(found)):
        parser.error("There's no meeting with that name")
    lazyMeetings.join_meeting(args.name)

def remove(args, parser):
    """Remove a link from the configuration file"""
    if(args.p and args.name == "false"):
        parser.error("The path and the software name were not specified")
    elif(args.p and args.name == "false"):
        parser.error("The software name was not specified")
    found = lazyMeetings.exists_meeting_list(args.name)
    if(not(found)):
        parser.error("There's no meeting with that name")
    lazyMeetings.remove_meeting(args.name)

def show_system_info(args):
    print(f"Operating system: {lazyMeetings.os_name}\nUser: {lazyMeetings.user}")

def list_(args):
    if(len(lazyMeetings.meeting_list) == 0):
        print("There's no meetings. You can add one by using the add command with the -p flag, followed by the meeting name and link")
    else:
        print("Meeting list:")
        for i in lazyMeetings.meeting_list:
            print(f"{i.name} -> {i.link}")

def add(args, parser):
    """Add a software_name/path pair to the "Meetings" setting in the configuration file"""
    if(args.p and args.name == "false"):
        parser.error("The name of the software was not provided")
    if(args.p and args.link == "false"):
        parser.error("The path was not provided")

    # This checks that the URL has both a scheme (e.g., http or https) and a network location (e.g., example.com)
    parsed_link = urlparse(args.link)
    if(not(all([parsed_link.scheme, parsed_link.netloc]))):
        parser.error("The link does not follow a proper link format")
        
    #Validates if the name or link is already in the json file
    for i in lazyMeetings.meeting_list:
        if(i.name == args.name):
            parser.error("The meeting name has been added in the past")
        elif(i.link == args.link):
            parser.error("The link has been added in the past")

    lazyMeetings.add_meeting(meetings.meeting(args.name, args.link))
    print(f"The {args.name} meeting has been added!")
