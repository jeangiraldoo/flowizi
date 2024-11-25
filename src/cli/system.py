from core.platform.info import operating_system, user


def show_system_info_command(args, parser):
    print(f"Operating system: {operating_system}\nUser: {user}")
