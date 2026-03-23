from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# ls takes no parameters — empty args list and parse_arguments does nothing
class LsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the ls command with Mythic.
class LsCommand(CommandBase):
    cmd = "ls"
    needs_admin = False
    help_cmd = "ls"
    description = "List the contents of a directory.\n"
    version = 1
    author = "@arsic"
    attackmapping = ["T1083"]
    argument_class = LsArguments
    attributes = CommandAttributes(
        builtin=True
    )

    # No pre-task logic needed — just acknowledge and let it through to the agent
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        return PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)