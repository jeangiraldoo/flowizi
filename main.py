from argparse import ArgumentParser
from commands import commands

parser = ArgumentParser(prog = "Lazy Meetings", description = "Automates the process of joining regular meetings")
parser.add_argument("-v", action = "store_true", help = "show the app version", default = False)

subparsers = parser.add_subparsers(dest = "command")

subparser_system = subparsers.add_parser("system", help = "show system-specific information")
subparser_system.set_defaults(func = commands.show_system_info)

subparser_add = subparsers.add_parser("add", help = "add a meeting link to the configuration file")
subparser_add.add_argument("-p", required = True, action = "store_true", help = "show the User-defined paths", default = False)
subparser_add.add_argument("name", type = str, nargs = "?", default = "false")
subparser_add.add_argument("link", type = str, nargs = "?", default = "false")
subparser_add.set_defaults(func = lambda args: commands.add(args, subparser_add))

subparser_list = subparsers.add_parser("list", help = "show all the meetings added")
subparser_list.add_argument("-d", action = "store_true", help = "show meetings available", default = False)
subparser_list.set_defaults(func = commands.list_)

subparser_remove = subparsers.add_parser("remove", help = "remove the selected link from the system")
subparser_remove.add_argument("-p", action = "store_true", help = "removes a meeting link from the list", default = False)
subparser_remove.add_argument("software_name", nargs = "?", default = "false")
subparser_remove.set_defaults(func = lambda args: commands.remove(args, subparser_remove))

subparser_join_meeting = subparsers.add_parser("join", help = "join the specified meeting")
subparser_join_meeting.add_argument("name", nargs = "?", default = "false")
subparser_join_meeting.set_defaults(func = lambda args: commands.join(args, subparser_join_meeting))

args = parser.parse_args() 

if hasattr(args, "func"):
    args.func(args)
else:
    commands.handle_arguments(args)
