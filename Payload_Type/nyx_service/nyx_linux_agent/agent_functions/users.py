from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# users takes no parameters — empty args list and parse_arguments does nothing
class UsersArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the users command with Mythic
class UsersCommand(CommandBase):
    cmd = "users"
    needs_admin = False
    help_cmd = "users"
    description = "List user accounts on the target (root + UID >= 1000)."
    version = 1
    author = "@arsic"
    attackmapping = ["T1087.001"]
    argument_class = UsersArguments

    # No pre-task logic needed — just acknowledge and let it through to the agent
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        return PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
