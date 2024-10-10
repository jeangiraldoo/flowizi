from src.flowizi import flowizi


def start(args, parser):
    if not flowizi.json.exists_environment(args.name):
        parser.error("The environment specified does not exist")

    for environment in flowizi.environment_list:
        if environment.name == args.name:
            environment.start()
            break
