from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

# This code is largely boilerplate and copied from shell.py in ExampleContainers repo

# Defines the parameters this command accepts. Mythic uses this to render
# the UI form and validate input before the task ever reaches the agent.
class ShellArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        # Must call super().__init__ first — sets up self.command_line (raw operator input)
        # and other internal Mythic states this class depends on
        super().__init__(command_line, **kwargs)

        # Each CommandParameter defines one input field in the Mythic UI
        self.args = [
            CommandParameter(
                name="command",          # key used to retrieve this value via get_arg("command")
                display_name="Command",  # label shown in the UI form
                type=ParameterType.String,
                description="Shell command to run on the target",
            )
        ]

    # Called by Mythic when the operator types the command as free text: "shell whoami"
    # self.command_line contains the raw text after the command name ("whoami")
    async def parse_arguments(self):
        if len(self.command_line) == 0:
            raise ValueError("Must supply a command to run")
        # Store the raw input under the "command" key for retrieval in create_go_tasking
        self.add_arg("command", self.command_line)

    # Called by Mythic instead of parse_arguments when input comes from the UI modal form
    # (structured JSON rather than free text). load_args_from_dictionary matches
    # JSON keys to self.args entries automatically.
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers this command with Mythic. Mythic discovers this class at startup by scanning
# agent_functions for any class that inherits CommandBase.
class ShellCommand(CommandBase):
    cmd = "shell"           # must match task.get("command") in agent.py exactly
    needs_admin = False     # if True, Mythic warns when callback is not elevated
    help_cmd = "shell <command>"
    description = "Execute a shell command on the target and return the output."
    version = 1
    author = "@arsic"
    attackmapping = ["T1059.004"]   # MITRE ATT&CK technique shown in the UI
    argument_class = ShellArguments # links this command to its parameter definition above

    # Called by Mythic on the service side BEFORE the task is sent to the agent.
    # Used to validate, log, or modify the task. Must return Success=True for the
    # task to proceed. DisplayParams controls what the UI shows next to the task entry.
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        # Show the actual command in the UI instead of raw JSON
        response.DisplayParams = taskData.args.get_arg("command")
        return response

    # Called by Mythic AFTER the agent posts output back via post_response.
    # Basic commands just acknowledge success. Advanced commands use this to parse
    # structured output and populate UI features like the file browser or process list.
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
