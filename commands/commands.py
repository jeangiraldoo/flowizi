import os
import platform
import meetings
from config import setup
from urllib.parse import urlparse
from app_data.lazymeetings import lazyMeetings

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
    found = False

    for i in lazyMeetings.meeting_list:
        if(i.name == args.software_name):
            lazyMeetings.remove_meeting(args.software_name)
            found = True
            break
    if(not(found)):
        parser.error("There's no meeting with that name")

def show_system_info(args):
    print(f"Operating system: {lazyMeetings.os_name}\nUser: {lazyMeetings.user}")

def list_(args):
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
