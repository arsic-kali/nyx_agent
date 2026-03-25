from mythic_container.MythicCommandBase import CommandBase, TaskArguments, ParameterType

class EnumHostArguments(TaskArguments):
    def __init__(self, command_line, **kwargs):
        super().__init__(command_line, **kwargs)

    async def parse_arguments(self):
        self.add_arg(
            name="mode",
            type=ParameterType.String,
            description="Enumeration mode: quick (default) or full",
            default_value="quick"
        )
        if self.command_line:
            self.add_arg("mode", self.command_line.strip())


class EnumHostCommand(CommandBase):
    cmd = "enum_host"
    needs_admin = False
    help_cmd = "enum_host [quick|full]"
    description = "Enumerate host information (system, user, network, files, etc.)"
    version = 1
    author = "@meisty"
    argument_class = EnumHostArguments
