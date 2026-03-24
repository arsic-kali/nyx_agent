from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *


# Defines the script file picker and optional args field rendered in the Mythic UI for this command
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

    # Called when input arrives from the UI modal form — maps JSON keys to self.args entries
    async def parse_dictionary(self, dictionary_arguments):
        self.load_args_from_dictionary(dictionary_arguments)


# Registers the runpy command with Mythic
class RunpyCommand(CommandBase):
    cmd = "runpy"
    needs_admin = False
    help_cmd = "runpy"
    description = "Transfer a Python script from the operator machine to the target and execute it, returning the output."
    version = 1
    author = "@arsic"
    attackmapping = ["T1059.006"]
    argument_class = RunpyArguments

    # Compiles the uploaded script into a standalone binary with PyInstaller so the target
    # needs no Python installation. Replaces the script file_id with the compiled binary's
    # file_id before the task is dispatched to the agent.
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        import os, shutil, subprocess, tempfile
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        file_id = taskData.args.get_arg("file")
        args    = taskData.args.get_arg("args")

        # Fetch the script bytes from Mythic
        file_resp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(AgentFileId=file_id))
        if not file_resp.Success:
            response.Success = False
            response.Error = f"failed to fetch script: {file_resp.Error}"
            return response

        build_dir = tempfile.mkdtemp()
        try:
            script_path = os.path.join(build_dir, "nyx_script.py")
            with open(script_path, "wb") as fh:
                fh.write(file_resp.Content)

            dist_dir = os.path.join(build_dir, "dist")
            result = subprocess.run(
                [
                    "pyinstaller", "--onefile",
                    "--distpath", dist_dir,
                    "--workpath", os.path.join(build_dir, "work"),
                    "--specpath", os.path.join(build_dir, "spec"),
                    "nyx_script.py",
                ],
                cwd=build_dir,
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                response.Success = False
                response.Error = f"PyInstaller failed:\n{result.stderr}"
                return response

            with open(os.path.join(dist_dir, "nyx_script"), "rb") as fh:
                binary = fh.read()

            # Register the compiled binary with Mythic and swap in its file_id
            create_resp = await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
                TaskID=taskData.Task.ID,
                FileContents=binary,
                DeleteAfterFetch=True,
            ))
            if not create_resp.Success:
                response.Success = False
                response.Error = f"failed to register binary: {create_resp.Error}"
                return response

            taskData.args.set_arg("file", create_resp.AgentFileId)
            response.DisplayParams = f"args: {args}" if args else "(compiled)"

        finally:
            shutil.rmtree(build_dir, ignore_errors=True)

        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
