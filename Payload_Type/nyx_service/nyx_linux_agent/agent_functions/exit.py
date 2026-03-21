from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Exit takes no parameters — empty args list and parse_arguments does nothing
class ExitArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = []

    async def parse_arguments(self):
        pass


# Registers the exit command with Mythic.
# supported_ui_features = ["callback_table:exit"] tells Mythic to show the exit
# button on the callback table row for this agent, wiring it to this command.
# builtin=True marks it as a core command that is always present on the agent.
class ExitCommand(CommandBase):
    cmd = "exit"
    needs_admin = False
    help_cmd = "exit"
    description = "Task the agent to exit and terminate the callback.\n"
    version = 1
    author = "@arsic"
    attackmapping = []
    argument_class = ExitArguments
    supported_ui_features = ["callback_table:exit"]
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
