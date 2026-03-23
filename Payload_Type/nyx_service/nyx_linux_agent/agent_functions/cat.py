from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# cat takes a raw free-text path — empty args list means Mythic sends the operator's input as a plain string
class CatArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the cat command with Mythic
class CatCommand(CommandBase):
    cmd = "cat"
    needs_admin = False
    help_cmd = "cat <path>"
    description = "Read and return the contents of a file on the target."
    version = 1
    author = "@arsic"
    attackmapping = ["T1005"]
    argument_class = CatArguments

    # Echoes the file path in the Mythic UI task entry so the operator can see what was read
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        response.DisplayParams = taskData.args.command_line
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
