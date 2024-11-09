from flowizi import flowizi
from core.database import validations


def start_command(args, parser):
    if not validations.env_exists(args.name):
        parser.error("The environment specified does not exist")

    for environment in flowizi.environment_list:
        if environment.name == args.name:
            environment.start()
            break
