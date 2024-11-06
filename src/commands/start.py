from flowizi import flowizi
from core.database import database


def start(args, parser):
    if not database.get_environment_ID(args.name):
        parser.error("The environment specified does not exist")

    for environment in flowizi.environment_list:
        if environment.name == args.name:
            environment.start()
            break
