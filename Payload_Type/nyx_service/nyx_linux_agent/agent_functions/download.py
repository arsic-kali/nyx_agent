from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the source path and optional destination label fields rendered in the Mythic UI for this command
class DownloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="path",
                display_name="Source Path",
                type=ParameterType.String,
                description="Absolute path of the file to download from the target",
            ),
            CommandParameter(
                name="dest",
                display_name="Dest Path",
                type=ParameterType.String,
                description="Optional filename/path label for the file as it appears in Mythic's Files tab",
                default_value="",
            ),
        ]

    # Called when the operator types the command as free text — stores the raw input as "path"
    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a file path")
        self.add_arg("path", self.command_line)

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the download command with Mythic
class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download <path>"
    description = "Download a file from the target machine to the Mythic server."
    version = 1
    author = "@arsic"
    attackmapping = ["T1041"]
    argument_class = DownloadArguments

    # Shows source -> dest (or just source) in the Mythic UI task entry
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        src = taskData.args.get_arg("path")
        dest = taskData.args.get_arg("dest")
        response.DisplayParams = f"{src} -> {dest}" if dest else src
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
