from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class UploadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file",
                display_name="File",
                type=ParameterType.File,
                description="File to upload to the target machine",
            ),
            CommandParameter(
                name="dest",
                display_name="Destination Path",
                type=ParameterType.String,
                description="Absolute path where the file should be written on the target",
            ),
        ]

    async def parse_arguments(self):
        pass

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class UploadCommand(CommandBase):
    cmd = "upload"
    needs_admin = False
    help_cmd = "upload"
    description = "Upload a file from the operator machine to the target machine."
    version = 1
    author = "@arsic"
    attackmapping = ["T1105"]
    argument_class = UploadArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        dest = taskData.args.get_arg("dest")
        response.DisplayParams = dest
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
