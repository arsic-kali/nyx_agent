from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the source directory and destination path fields rendered in the Mythic UI
class ZipArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="src",
                display_name="Source Directory",
                type=ParameterType.String,
                description="Path to the directory to zip on the target",
            ),
            CommandParameter(
                name="dest",
                display_name="Destination Path",
                type=ParameterType.String,
                description="Path where the zip file should be saved on the target (e.g. /tmp/out.zip)",
            ),
        ]

    async def parse_arguments(self):
        pass

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the zip command with Mythic
class ZipCommand(CommandBase):
    cmd = "zip"
    needs_admin = False
    help_cmd = "zip"
    description = "Recursively zip a directory on the target and save it to a specified path. Use download afterwards to retrieve the archive."
    version = 1
    author = "@arsic"
    attackmapping = ["T1560.002"]
    argument_class = ZipArguments

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
