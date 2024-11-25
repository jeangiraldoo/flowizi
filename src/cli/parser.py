from typing import Callable
from enum import Enum
from dataclasses import dataclass
from abc import ABC, abstractmethod
from argparse import ArgumentParser
from cli import add, remove, list, system, start, record


class CmdType(Enum):
    """Represents all of the commands currently available in the application."""
    ADD = "add"
    LIST = "list"
    REMOVE = "remove"
    SYSTEM = "system"
    RECORD = "record"
    START = "start"


@dataclass
class CmdParserData():
    """Represents the data necessary to create a command parser."""
    cmd_type: CmdType
    help: str
    func: Callable
    is_name_arg_optional: bool


class CmdParser(ABC):
    """Configures all command parsers for use in the CLI.

    This class serves as a base for configuring the main parser and subparsers 
    for handling command-line arguments. It defines the available arguments for
    each command and associates it with a handler function that is called 
    when the command is invoked by the user.
    """
    parser = ArgumentParser(
            prog="Flowizi",
            description="Automates the process of starting up your workflow"
        )

    @abstractmethod
    def init():
        """
        Sets up the main parser and command subparsers to process arguments.
        """
        CmdParser.parser.add_argument(
            "-v", action="store_true", help="show the app version",
            default=False
            )

        subparser = CmdParser.parser.add_subparsers(dest="command")

        # commands related to elements in general
        elem_cmds = [
            CmdParserData(cmd_type=CmdType.ADD, func=add.add_command,
                          help="Add an element (environment, website, application or file)",
                          is_name_arg_optional=False),
            CmdParserData(cmd_type=CmdType.LIST, func=list.list_command,
                          help="Display all added environments",
                          is_name_arg_optional=True),
            CmdParserData(cmd_type=CmdType.REMOVE, func=remove.remove_command,
                          help="Remove the selected environment from the system",
                          is_name_arg_optional=False)
        ]

        # commands related to environments specifically or unrelated to contained elements
        env_cmds = [
            CmdParserData(cmd_type=CmdType.SYSTEM, func=system.show_system_info_command,
                          help="Show system-specific information",
                          is_name_arg_optional=True),
            CmdParserData(cmd_type=CmdType.START, func=start.start_command,
                          help="Start the specified environment",
                          is_name_arg_optional=False),
            CmdParserData(cmd_type=CmdType.RECORD, func=record.record_command,
                          help="Toogle on/off screen recording for an environment",
                          is_name_arg_optional=False)
        ]

        CmdParser._setup_env_subparsers(subparser, env_cmds)
        CmdParser._setup_elem_subparsers(subparser, elem_cmds)

    def _setup_env_subparsers(subparser, env_cmds):
        """
        Configures subparsers for commands unrelated to contained elements.

        Args:
            subparser: Main command subparser.
            env_cmds (list[dict]): Dictionary list where each one contains
                                   the necessary data to built a subparser.
        """
        for cmd in env_cmds:
            cmd_name = cmd.cmd_type.value
            parser = subparser.add_parser(cmd_name, help=cmd.help)

            if not cmd.is_name_arg_optional:
                parser.add_argument("name")

            if cmd_name == "record":
                record_group = parser.add_mutually_exclusive_group(required=True)
                record_group.add_argument("-t", action="store_true")
                record_group.add_argument("-f", action="store_true")

            CmdParser._set_defaults(parser, cmd.func)

    def _setup_elem_subparsers(subparser, elem_cmds):
        """
        Configures subparsers for commands related to contained elements.

        Args:
            env_cmds (list[dict]): Dictionary list where each one contains
                                   the necessary data to built a subparser.
        """
        for cmd in elem_cmds:
            cmd_name = cmd.cmd_type.value
            parser = subparser.add_parser(cmd_name, help=cmd.help)

            if cmd.is_name_arg_optional:
                CmdParser._setup_optional_name(parser)
            else:
                CmdParser._setup_required_name(parser, cmd.cmd_type)

            CmdParser._set_defaults(parser, cmd.func)

    def _setup_optional_name(parser):
        """
        Configures a parser for commands where the "name" argument is optional.

        Args:
            parser: Command-specific parser to which arguments will be added.
        """
        parser.add_argument("name", nargs="?")
        parser.add_argument("-w", "--website", dest="w", action="store_true")
        parser.add_argument("-f", "--file", dest="f", action="store_true")
        parser.add_argument("-a", "--application", dest="a", action="store_true")

    def _setup_required_name(parser, cmd_type: CmdType):
        """
        Configures a parser for commands where the "name" argument is mandatory.

        Args:
            parser: Command-specific parser to which arguments will be added.
            cmd_type (CmdType): Represents the command associated with the parser.
        """
        parser.add_argument("name")
        parser.add_argument("-w", "--website", dest="w", default=False)
        parser.add_argument("-f", "--file", dest="f", default=False)

        if cmd_type == CmdType.ADD:
            parser.add_argument("-a", "--application", dest="a", action="store_true")
        else:
            parser.add_argument("-a", "--application", dest="a", default=False)

    def _set_defaults(parser, command: Callable):
        """
        Configures the default action for a parser by associating a command function.

        Args:
            command (Callable): Function that will process the arguments.
        """
        parser.set_defaults(func=lambda args: command(args, parser))


CmdParser.init()
parsed_arg = CmdParser.parser.parse_args()
