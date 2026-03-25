from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *

# pspawn takes no parameters — the agent re-executes itself with no operator input required
class PspawnArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        # Must call super().__init__ first — sets up self.command_line and other internal Mythic state
        super().__init__(command_line, **kwargs)
        self.args = []  # no parameters

    async def parse_arguments(self):
        pass  # nothing to parse

# Registers this command with Mythic. Mythic discovers this class at startup by scanning
# agent_functions for any class that inherits CommandBase.
class PspawnCommand(CommandBase):
    cmd = "pspawn"          # must match task.get("command") in agent.py exactly
    needs_admin = False     # if True, Mythic warns when callback is not elevated
    help_cmd = "pspawn"
    description = "Spawn a new agent instance as a separate process."
    version = 1
    author = "@arsic"
    argument_class = PspawnArguments    # links this command to its parameter definition above
    attackmapping = ["T1543"]           # MITRE ATT&CK technique shown in the UI
    attributes = CommandAttributes(
        builtin=True
    )

    # Called by Mythic on the service side BEFORE the task is sent to the agent.
    # No validation needed here since pspawn takes no parameters.
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(
            TaskID=taskData.Task.ID,
            Success=True,
        )
        return response

    # Called by Mythic AFTER the agent posts output back via post_response.
    # Simply acknowledges success — the new callback appearing in the UI confirms the spawn worked.
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        resp = PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
        return resp