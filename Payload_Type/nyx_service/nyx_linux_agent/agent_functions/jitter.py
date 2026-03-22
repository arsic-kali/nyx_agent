from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class JitterArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


class JitterCommand(CommandBase):
    cmd = "jitter"
    needs_admin = False
    help_cmd = "jitter <percentage>"
    description = "Set the agent jitter percentage.\n"
    version = 1
    author = "@arsic"
    attackmapping = []
    argument_class = JitterArguments
    attributes = CommandAttributes(
        builtin=True
    )

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        return PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
