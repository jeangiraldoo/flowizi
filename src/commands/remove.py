from src.flowizi import flowizi


def remove(args, parser):
    """Remove a link from the configuration file"""
    if not flowizi.json.exists_environment(args.name):
        parser.error("There's no environment with that name")

    if args.w:
        remove_website(parser, args.name, args.w)
    elif args.f:
        remove_file(parser, args.name, args.f)
    elif args.a:
        remove_app(parser, args.name, args.a)
    else:
        remove_environment(args.name)


def remove_environment(name):
    flowizi.json.remove_environment(name)


def remove_website(parser, env_name, name):
    if not flowizi.json.exists_environment_element(env_name, "websites", name):
        parser.error("The element specfified does not exist")

    flowizi.json.remove_environment_element(env_name, "websites", name)


def remove_file(parser, env_name, name):
    if not flowizi.json.exists_environment_element(env_name, "files", name):
        parser.error("The element specfified does not exist")

    flowizi.json.remove_environment_element(env_name, "files", name)


def remove_app(parser, env_name, name):
    if not flowizi.json.exists_environment_element(env_name, "applications", name):
        parser.error("The element specfified does not exist")

    flowizi.json.remove_environment_element(env_name, "applications", name)
