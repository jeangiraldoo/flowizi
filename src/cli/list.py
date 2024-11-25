from flowizi import flowizi
from core.database.validations import Validations
from core.elements.element import ElemType


def list_command(args, parser):
    if len(flowizi.environment_list) == 0:
        print("There's no environments. You can add one by using the add command, followed by the environment name")
    elif args.name and not Validations.env_exists(args.name):
        parser.error("The environment specified does not exist")
    elif args.w:
        list_contained_elements(args.name, ElemType.WEB)
    elif args.f:
        list_contained_elements(args.name, ElemType.FILE)
    elif args.a:
        list_contained_elements(args.name, ElemType.APP)
    elif args.name:
        list_contained_elements(args.name, ElemType.WEB)
        list_contained_elements(args.name, ElemType.FILE)
        list_contained_elements(args.name, ElemType.APP)
    else:
        list_environments()


def list_environments():
    print("Environment list:")
    for environment in flowizi.environment_list:
        print(f"{environment.name} [websites: {len(environment.websites)},",
              f"files: {len(environment.files)},",
              f"apps: {len(environment.applications)},",
              f"record screen: {environment.record}]")


def list_contained_elements(env_name: str, element_type: ElemType):
    env = ""
    for environment in flowizi.environment_list:
        if environment.name == env_name:
            env = environment
            break

    elements = getattr(env, element_type.value)

    if len(elements) == 0:
        print(f"No {element_type.value} in the {env_name} environment")
    else:
        print(f"\n{element_type.value.capitalize()} in the {env_name} environment:")
        for element in elements:
            print(f"{element.name} -> {element.url}")
