from flowizi import flowizi


def record(args, parser):
    if not flowizi.json.exists_environment(args.name):
        parser.error("There's no environment with that name")
    if args.t:
        toogle_on(args.name)
    elif args.f:
        toogle_off(args.name)


def toogle_on(name):
    if not flowizi.json.verify_environment_recording(True, name):
        print(f"Error. The {name} environment is set to record the screen")
    else:
        flowizi.json.update_environment_record(True, name)
        print(f"The {name} environment is now set to record the screen")


def toogle_off(name):
    if not flowizi.json.verify_environment_recording(False, name):
        print(f"Error. The {name} environment is set to not record the screen")
    else:
        flowizi.json.update_environment_record(False, name)
        print(f"The {name} environment is now set to not record the screen")
