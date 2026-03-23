from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the multi-file picker rendered in the Mythic UI for this command
class CampaignArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="files",
                display_name="Scripts",
                type=ParameterType.FileMultiple,
                description="Python scripts to execute on the target in the order selected",
            ),
        ]

    async def parse_arguments(self):
        pass

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the campaign command with Mythic
class CampaignCommand(CommandBase):
    cmd = "campaign"
    needs_admin = False
    help_cmd = "campaign"
    description = "Transfer and execute multiple Python scripts on the target in sequence, reporting each result separately."
    version = 1
    author = "@arsic"
    attackmapping = ["T1059.006"]
    argument_class = CampaignArguments
    # Shows the script count in the Mythic UI task entry so the operator can see how many scripts will run
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        files = taskData.args.get_arg("files")
        count = len(files) if files else 0
        response.DisplayParams = f"{count} script{'s' if count != 1 else ''}"
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
