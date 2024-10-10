from src.flowizi import flowizi


def remove(args, parser):
    """Remove a link from the configuration file"""
    if not flowizi.json.exists_environment(args.name):
        parser.error("There's no environment with that name")

    if args.w != "false":
        remove_website(parser, args.name, args.w)
    else:
        remove_environment(args.name)


def remove_environment(name):
    flowizi.json.remove_environment(name)


def remove_website(parser, env_name, name):
    if not flowizi.json.exists_environment_element(env_name, "websites", name):
        parser.error("The element specfified does not exist")

    flowizi.json.remove_environment_element(env_name, "websites", name)
