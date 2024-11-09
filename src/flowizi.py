from core.database.validations import Validations


class Flowizi:
    def __init__(self):
        self.version = "1.4.0-alpha"
        self.environment_list = Validations.get_envs()

    def update_environments(self):
        """Gets the current environments in the database and updates
        the environment_list attribute"""
        self.environment_list = Validations.get_envs()


flowizi = Flowizi()
