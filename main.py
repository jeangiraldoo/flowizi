from argparse import ArgumentParser
from src.commands import commands

parser = ArgumentParser(prog = "Lazy Meetings", description = "Automates the process of joining regular meetings")
parser.add_argument("-v", action = "store_true", help = "show the app version", default = False)

subparsers = parser.add_subparsers(dest = "command")

subparser_system = subparsers.add_parser("system", help = "show system-specific information")
subparser_system.set_defaults(func = commands.show_system_info)

subparser_add = subparsers.add_parser("add", help = "add a meeting link to the configuration file")
subparser_add.add_argument("name", type = str, default = "false")
subparser_add.add_argument("-w", "--website", nargs = 2, metavar = ("website_name", "link"), dest = "w", default = "false")
subparser_add.set_defaults(func = lambda args: commands.add(args, subparser_add))

subparser_list = subparsers.add_parser("list", help = "show all the meetings added")
subparser_list.set_defaults(func = commands.list_)

subparser_remove = subparsers.add_parser("remove", help = "remove the selected environment from the system")
subparser_remove.add_argument("name", default = "false")
subparser_remove.add_argument("-w", "--website", type = str, dest = "w", default = "false")
subparser_remove.set_defaults(func = lambda args: commands.remove(args, subparser_remove))

subparser_start_meeting = subparsers.add_parser("start", help = "start the specified environment")
subparser_start_meeting.add_argument("name", default = "false")
subparser_start_meeting.set_defaults(func = lambda args: commands.start(args, subparser_start_meeting))

subparser_record = subparsers.add_parser("record", help = "decide if you want to record the screen when an environment is started or not to do so")
subparser_record.add_argument("name", default = "false")
record_group = subparser_record.add_mutually_exclusive_group(required = True)
record_group.add_argument("-t", action = "store_true")
record_group.add_argument("-f", action = "store_true")
subparser_record.set_defaults(func = lambda args: commands.record(args, subparser_record))

args = parser.parse_args() 

if hasattr(args, "func"):
    args.func(args)
else:
    commands.handle_arguments(args)
