from flowizi import flowizi
from cli.parser import parsed_arg
from gui.controllers.controller import Controller

if hasattr(parsed_arg, "func"):
    parsed_arg.func(parsed_arg)
elif parsed_arg.v:
    print(f"Flowizi {flowizi.version}")
elif parsed_arg.command is None:
    controller = Controller().main()
