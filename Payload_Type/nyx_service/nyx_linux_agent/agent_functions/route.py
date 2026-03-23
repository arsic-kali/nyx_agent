from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

# route takes no parameters — empty args list and parse_arguments does nothing
class RouteArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the route command with Mythic.
class RouteCommand(CommandBase):
    cmd = "route"
    needs_admin = False
    help_cmd = "route"
    description = "Display routing table information.\n"
    version = 1
    author = "@arsic"
    attackmapping = ["T1016"]
    argument_class = RouteArguments
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