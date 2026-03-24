from mythic_container.MythicCommandBase import (
    CommandBase,
    TaskArguments,
    ParameterType,
)

class EnumHostArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)
        # Define a single string parameter called "mode"
        self.args = [
            {
                "name": "mode",
                "type": ParameterType.String,
                "description": "Enumeration mode: quick (default) or full",
                "default_value": "quick",
            }
        ]

    async def parse_arguments(self):
        """
        Parse the input command line from Mythic into parameters
        """
        if self.command_line:
            self.add_arg("mode", self.command_line.strip())


class EnumHostCommand(CommandBase):
    cmd = "enum_host"  # Command name in Mythic
    needs_admin = False
    help_cmd = "enum_host [quick|full]"
    description = "Enumerate host information (system, user, network, files, etc.)"
    version = 1
    author = "@meisty"
    argument_class = EnumHostArguments
