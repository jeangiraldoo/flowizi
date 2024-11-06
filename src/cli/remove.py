from flowizi import flowizi
from core.database import database


def remove_command(args, parser):
    """Remove a link from the configuration file"""
    if not flowizi.json.exists_environment(args.name):
        parser.error("There's no environment with that name")

    if args.w:
        remove_website(parser, args.name, args.w)
    elif args.f:
        remove_file(parser, args.name, args.f)
    elif args.a:
        remove_application(parser, args.name, args.a)
    else:
        remove_environment(args.name)


def remove_environment(name):
    database.delete_environment(name)


def remove_website(parser, env_name, name):
    id = database.get_environment_ID(env_name)
    if not id and parser:
        parser.error("The element specfified does not exist")

    database.delete_element(env_name, "websites", name)


def remove_file(parser, env_name, name):
    id = database.get_environment_ID(env_name)
    if not id and parser:
        parser.error("The element specfified does not exist")

    database.delete_element(env_name, "files", name)


def remove_application(parser, env_name, name):
    id = database.get_environment_ID(env_name)
    if not id and parser:
        parser.error("The element specfified does not exist")

    database.delete_element(env_name, "applications", name)
