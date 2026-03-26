from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class EnumHostArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="mode",
                display_name="Mode",
                type=ParameterType.String,
                description="Enumeration mode: quick (default) or full",
                default_value="quick",
            )
        ]

    async def parse_arguments(self):
        pass

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class EnumHostCommand(CommandBase):
    cmd = "enum_host"
    needs_admin = False
    help_cmd = "enum_host [quick|full]"
    description = "Enumerate host information (system, user, network, files, processes, secrets, etc.)"
    version = 1
    author = "@meisty"
    attackmapping = ["T1082", "T1033", "T1049", "T1057", "T1083"]
    argument_class = EnumHostArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        mode = taskData.args.get_arg("mode") or "quick"
        response.DisplayParams = mode
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
