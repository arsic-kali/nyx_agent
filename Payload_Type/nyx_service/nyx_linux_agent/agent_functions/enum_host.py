from mythic_container.MythicCommandBase import *

class EnumHostArguments(TaskArguments):
    def __init__(self):
        super().__init__()
        self.args = []

class EnumHostCommand(CommandBase):
    cmd = "enum_host"
    needs_admin = False
    help_cmd = "enum_host"
    description = "Enumerate host information (system, user, network, processes)"
    version = 1
    author = "@meisty"

    argument_class = EnumHostArguments

    async def create_tasking(self, task):
        return task
