import json
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the source directory field rendered in the Mythic UI
class BulkDownloadArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="src",
                display_name="Source Directory",
                type=ParameterType.String,
                description="Directory on the target to recursively download all files from",
            ),
        ]

    async def parse_arguments(self):
        pass

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the bulk_download command with Mythic
class BulkDownloadCommand(CommandBase):
    cmd = "bulk_download"
    needs_admin = False
    help_cmd = "bulk_download"
    description = "Recursively download all files in a directory from the target to Mythic. Each file appears separately in Mythic's Files tab."
    version = 1
    author = "@arsic"
    attackmapping = ["T1560", "T1030"]
    argument_class = BulkDownloadArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        src = taskData.args.get_arg("src")
        response.DisplayParams = src
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
