from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the IP, port, and protocol fields rendered in the Mythic UI for this command
class ConnectArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="ip",
                display_name="IP",
                type=ParameterType.String,
                description="Listener IP address to connect back to",
            ),
            CommandParameter(
                name="port",
                display_name="Port",
                type=ParameterType.Number,
                description="Listener port to connect back to",
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


# Registers the connect command with Mythic
class ConnectCommand(CommandBase):
    cmd = "connect"
    needs_admin = False
    help_cmd = "connect"
    description = "Initiate a reverse shell back to an operator-controlled listener over TCP or UDP."
    version = 1
    author = "@arsic"
    attackmapping = ["T1059.004", "T1071.001"]
    argument_class = ConnectArguments

    # Shows the target IP:port and protocol in the Mythic UI task entry
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
