from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the zip path and destination directory fields rendered in the Mythic UI
class UnzipArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="src",
                display_name="Zip File Path",
                type=ParameterType.String,
                description="Path to the zip file on the target to extract",
            ),
            CommandParameter(
                name="dest",
                display_name="Destination Directory",
                type=ParameterType.String,
                description="Directory on the target to extract the zip contents into",
            ),
        ]

    async def parse_arguments(self):
        pass

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the unzip command with Mythic
class UnzipCommand(CommandBase):
    cmd = "unzip"
    needs_admin = False
    help_cmd = "unzip"
    description = "Extract a zip archive on the target to a specified directory."
    version = 1
    author = "@arsic"
    attackmapping = ["T1560.002"]
    argument_class = UnzipArguments

    # Shows src -> dest in the Mythic UI task entry
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        src  = taskData.args.get_arg("src")
        dest = taskData.args.get_arg("dest")
        response.DisplayParams = f"{src} -> {dest}"
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
