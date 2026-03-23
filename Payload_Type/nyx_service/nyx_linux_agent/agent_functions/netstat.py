from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# netstat takes no parameters — empty args list and parse_arguments does nothing
class NetstatArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the netstat command with Mythic
class NetstatCommand(CommandBase):
    cmd = "netstat"
    needs_admin = False
    help_cmd = "netstat"
    description = "Display all TCP connections with process info (netstat -antlp)."
    version = 1
    author = "@arsic"
    attackmapping = ["T1049"]
    argument_class = NetstatArguments

    # No pre-task logic needed — just acknowledge and let it through to the agent
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        return PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
