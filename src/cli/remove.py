from core.database import database, validations


def remove_command(args, parser):
    """Remove a link from the configuration file"""
    if not database.get_element_ID("environments", args.name):
        parser.error("There's no environment with that name")

    if args.w:
        remove_element(parser, args.name, "websites", args.w)
    elif args.f:
        remove_element(parser, args.name, "files", args.f)
    elif args.a:
        remove_element(parser, args.name, "applications", args.a)
    else:
        remove_environment(args.name)


def remove_environment(name: str):
    """Removes an environment from the database through the CLI.

    Args:
        name (str): Name of the environment to remove.
    """
    result = validations.delete_env_validation(name)

    if result:
        print(f"The {name} environment was successfully removed!")


def remove_element(parser, env_name: str, elem_type: str, name: str):
    """Removes an element from the database through the CLI.

    Args:
        parser: Subparser object used for the remove command, used to show errors.
        env_name (str): Name of the environment that contains the element to remove.
        elem_type (str): Element type ("website", "file", or "application").
        name (str): Name of the element to remove.
    """
    singular_type = elem_type[:len(elem_type) - 1]

    result, status_msg = validations.delete_elem_validation(env_name, elem_type, name)
    if not result and status_msg == "no elem":
        parser.error(f"The {singular_type} specfified does not exist")

    print(f"The {name} {singular_type} was successfully removed from the {env_name} environment!")
