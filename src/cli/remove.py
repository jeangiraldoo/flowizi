from core.database.validations import Validations, ResType
from core.elements.element import ElemType


def remove_command(args, parser):
    """Remove a link from the configuration file"""
    if args.w:
        remove_element(parser, args.name, ElemType.WEB, args.w)
    elif args.f:
        remove_element(parser, args.name, ElemType.FILE, args.f)
    elif args.a:
        remove_element(parser, args.name, ElemType.APP, args.a)
    else:
        remove_environment(parser, args.name)


def remove_environment(parser, name: str):
    """Removes an environment from the database.

    Args:
        name (str): Name of the environment to remove.
    """
    result = Validations.delete_env_validation(name)

    if result:
        print(f"The {name} environment was successfully removed!")
    else:
        parser.error(f"There is no environment called {name}")


def remove_element(parser, env_name: str, elem_type: ElemType, name: str):
    """Removes an element from the database.

    Args:
        parser: Subparser object used for the remove command, used to show
                errors.
        env_name (str): Name of the environment that contains the element to
                remove.
        elem_type (ElemType): Element type (WEBSITE, FILE, or APP).
        name (str): Name of the element to remove.
    """
    singular_type = elem_type.value[:len(elem_type.value) - 1]

    result = Validations.delete_elem_validation(env_name, elem_type, name)
    if result == ResType.ENV_NOT_EXISTS:
        parser.error(f"There is no environment called {env_name}")
    elif result == ResType.ELEM_NOT_EXISTS:
        parser.error(f"The {singular_type} specfified does not exist")

    print(f"The {name} {singular_type} was successfully removed from the {env_name} environment!")
