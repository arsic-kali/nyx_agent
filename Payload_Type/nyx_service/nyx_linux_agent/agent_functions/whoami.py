from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Takes no args since its just getting current user
class WhoamiArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the whoami command with Mythic.
class LsCommand(CommandBase):
    cmd = "whoami"
    needs_admin = False
    help_cmd = "whoami"
    description = "Lists the current user\n"
    version = 1
    author = "@arsic"
    attackmapping = []
    argument_class = WhoamiArguments
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