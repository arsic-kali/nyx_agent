from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the path field rendered in the Mythic UI for this command
class CdArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                display_name="Path",
                type=ParameterType.String,
                description="Directory to change into",
            )
        ]

    # Called when the operator types the command as free text — stores the raw input as "path"
    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a path")
        self.add_arg("path", self.command_line)

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the cd command with Mythic
class CdCommand(CommandBase):
    cmd = "cd"
    needs_admin = False
    help_cmd = "cd <path>"
    description = "Change the agent's current working directory."
    version = 1
    author = "@arsic"
    attackmapping = ["T1083"]
    argument_class = CdArguments

    # Shows the target path in the Mythic UI task entry
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        response.DisplayParams = taskData.args.get_arg("path")
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
