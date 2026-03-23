from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the IP, port, and protocol fields rendered in the Mythic UI for this command
class BindshellArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="ip",
                display_name="IP",
                type=ParameterType.String,
                default_value="0.0.0.0",
                description="Interface to bind on (0.0.0.0 = all interfaces)",
            ),
            CommandParameter(
                name="port",
                display_name="Port",
                type=ParameterType.Number,
                description="Port to listen on",
            ),
            CommandParameter(
                name="protocol",
                display_name="Protocol",
                type=ParameterType.ChooseOne,
                choices=["TCP", "UDP"],
                default_value="TCP",
                description="Connection protocol",
            ),
        ]

    async def parse_arguments(self):
        pass

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the bindshell command with Mythic
class BindshellCommand(CommandBase):
    cmd = "bindshell"
    needs_admin = False
    help_cmd = "bindshell"
    description = "Open a bind shell on the target — operator connects inbound to the specified IP and port."
    version = 1
    author = "@arsic"
    attackmapping = ["T1059.004"]
    argument_class = BindshellArguments

    # Shows the bind address and protocol in the Mythic UI task entry
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        ip       = taskData.args.get_arg("ip")
        port     = taskData.args.get_arg("port")
        protocol = taskData.args.get_arg("protocol")
        response.DisplayParams = f"{ip}:{port} ({protocol})"
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
