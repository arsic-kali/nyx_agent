from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


class RunpyArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        self.args = [
            CommandParameter(
                name="file",
                display_name="Script",
                type=ParameterType.File,
                description="Python script to execute on the target machine",
            ),
            CommandParameter(
                name="args",
                display_name="Arguments",
                type=ParameterType.String,
                description="Optional command-line arguments to pass to the script",
            ),
        ]

    async def parse_arguments(self):
        pass

    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


class RunpyCommand(CommandBase):
    cmd = "runpy"
    needs_admin = False
    help_cmd = "runpy"
    description = "Transfer a Python script from the operator machine to the target and execute it, returning the output."
    version = 1
    author = "@arsic"
    attackmapping = ["T1059.006"]
    argument_class = RunpyArguments

    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        args = taskData.args.get_arg("args")
        response.DisplayParams = f"args: {args}" if args else ""
        return response

    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
