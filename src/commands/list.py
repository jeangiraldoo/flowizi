from src.app_core.flowizi import flowizi


def list_(args):
    if len(flowizi.environment_list) == 0:
        print("There's no environments. You can add one by using the add command, followed by the environment name")
    else:
        print("Environment list:")
        for environment in flowizi.environment_list:
            print(f"{environment.name}")
