from core.database.validations import ResultType


def get_pos(lower_range: int, upper_range: int) -> ResultType | int:
    """Prompts the user to input a number that matches one of the items being
    shown on the screen.

    This function is only called when using the CLI.

    Returns:
        int: The user's choice as an integer.
        ResultType: Enum that indicates the result of the operation.
    """
    try:
        pos = int(input("\nType the number associated with an option: "))
    except:
        print("You must type a number")
        exit(1)

    if pos < lower_range or pos > upper_range:
        return ResultType.INVALID_NUMBER
    return pos


def display_items(item_type: str, items: str | dict, list_type: str):
    if not items:
        print(f"No {item_type} found.")

    print(f"Detected {item_type}:\n")

    if list_type == "index":
        for idx, name in enumerate(items, start = 1):
            print(f"{idx}. {name}")
    else:
        for name in items:
            print(name)
