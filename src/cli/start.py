from flowizi import flowizi
from core.database.validations import Validations


def start_command(args, parser):
    if not Validations.env_exists(args.name):
        parser.error("The environment specified does not exist")

    for environment in flowizi.environment_list:
        if environment.name == args.name:
            environment.start()
            break
