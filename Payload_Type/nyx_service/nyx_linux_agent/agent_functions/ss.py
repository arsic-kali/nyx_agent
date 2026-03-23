from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# ss takes no parameters — empty args list and parse_arguments does nothing
class SsArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the ss command with Mythic
class SsCommand(CommandBase):
    cmd = "ss"
    needs_admin = False
    help_cmd = "ss"
    description = "Display listening and established sockets (ss -tulpn)."
    version = 1
    author = "@arsic"
    attackmapping = ["T1049"]
    argument_class = SsArguments

    # No pre-task logic needed — just acknowledge and let it through to the agent
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        return PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
