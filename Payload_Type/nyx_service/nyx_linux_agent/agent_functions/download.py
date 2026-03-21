from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


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

    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a file path")
        self.add_arg("path", self.command_line)

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class DownloadCommand(CommandBase):
    cmd = "download"
    needs_admin = False
    help_cmd = "download <path>"
    description = "Download a file from the target machine to the Mythic server."
    version = 1
    author = "@arsic"
    attackmapping = ["T1041"]
    argument_class = DownloadArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        src = taskData.args.get_arg("path")
        dest = taskData.args.get_arg("dest")
        response.DisplayParams = f"{src} -> {dest}" if dest else src
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
