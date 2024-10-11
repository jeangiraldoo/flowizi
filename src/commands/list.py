from src.flowizi import flowizi


def list_(parser, args):
    if len(flowizi.environment_list) == 0:
        print("There's no environments. You can add one by using the add command, followed by the environment name")

    if args.w:
        if not flowizi.json.exists_environment(args.name):
            parser.error("The environment specified does not exist")

        list_contained_elements(args.name, "websites")
    elif args.f:
        if not flowizi.json.exists_environment(args.name):
            parser.error("The environment specified does not exist")

        list_contained_elements(args.name, "files")
    elif args.a:
        if not flowizi.json.exists_environment(args.name):
            parser.error("The environment specified does not exist")

        list_contained_elements(args.name, "applications")
    elif args.name:
        if not flowizi.json.exists_environment(args.name):
            parser.error("The environment specified does not exist")

        list_contained_elements(args.name, "websites")
        list_contained_elements(args.name, "files")
        list_contained_elements(args.name, "applications")
    else:
        list_environments()


def list_environments():
    print("Environment list:")
    for environment in flowizi.environment_list:
        print(f"{environment.name} [websites: {len(environment.websites)},",
              f"files: {len(environment.files)},",
              f"apps: {len(environment.applications)},",
              f"record screen: {environment.record}]")


def list_contained_elements(env_name, element_type):
    env = ""
    for environment in flowizi.environment_list:
        if environment.name == env_name:
            env = environment
            break

    elements = getattr(env, element_type)

    if len(elements) == 0:
        print(f"No {element_type} in the {env_name} environment")
    else:
        print(f"\n{element_type.capitalize()} in the {env_name} environment:")
        for element in elements:
            print(f"{element.name} -> {element.url}")
