from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# passwd takes no parameters — empty args list and parse_arguments does nothing
class PasswdArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the passwd command with Mythic
class PasswdCommand(CommandBase):
    cmd = "passwd"
    needs_admin = False
    help_cmd = "passwd"
    description = "Dump the contents of /etc/passwd."
    version = 1
    author = "@arsic"
    attackmapping = ["T1003.008"]
    argument_class = PasswdArguments

    # No pre-task logic needed — just acknowledge and let it through to the agent
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        return PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
