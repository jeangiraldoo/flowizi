from argparse import ArgumentParser
from src.flowizi import flowizi
from src.commands import add
from src.commands import remove
from src.commands import list
from src.commands import system
from src.commands import start
from src.commands import record

parser = ArgumentParser(prog = "Flowizi", description = "Automates the process of starting up your workflow")
parser.add_argument("-v", action = "store_true", help = "show the app version", default = False)

subparsers = parser.add_subparsers(dest = "command")

subparser_system = subparsers.add_parser("system", help = "show system-specific information")
subparser_system.set_defaults(func = system.show_system_info)

subparser_add = subparsers.add_parser("add", help = "Add an element (environment, website, application or file)")
subparser_add.add_argument("name")
subparser_add.add_argument("-w", "--website", nargs = 1, dest = "w", default = False)
subparser_add.add_argument("-f", "--file", nargs = 1, dest = "f", default = False)
subparser_add.set_defaults(func = lambda args: add.add(args, subparser_add))

subparser_list = subparsers.add_parser("list", help = "show all the environments added")
subparser_list.set_defaults(func = list.list_)

subparser_remove = subparsers.add_parser("remove", help = "remove the selected environment from the system")
subparser_remove.add_argument("name")
subparser_remove.add_argument("-w", "--website", type = str, dest = "w", default = False)
subparser_remove.set_defaults(func = lambda args: remove.remove(args, subparser_remove))

subparser_start_meeting = subparsers.add_parser("start", help = "start the specified environment")
subparser_start_meeting.add_argument("name")
subparser_start_meeting.set_defaults(func = lambda args: start.start(args, subparser_start_meeting))

subparser_record = subparsers.add_parser("record", help = "toogle on/off screen recording for an environment")
subparser_record.add_argument("name")
record_group = subparser_record.add_mutually_exclusive_group(required = True)
record_group.add_argument("-t", action = "store_true")
record_group.add_argument("-f", action = "store_true")
subparser_record.set_defaults(func = lambda args: record.record(args, subparser_record))

args = parser.parse_args()

if hasattr(args, "func"):
    args.func(args)
else:
    if args.v:
        print(f"Flowizi {flowizi.version}")
