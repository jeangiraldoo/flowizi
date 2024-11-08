from flowizi import flowizi
from core.database import database


def start_command(args, parser):
    if not database.get_element_ID(args.name, "environments"):
        parser.error("The environment specified does not exist")

    for environment in flowizi.environment_list:
        if environment.name == args.name:
            environment.start()
            break
