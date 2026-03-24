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
    # Compiles each uploaded script into a standalone binary with PyInstaller, replacing
    # each script file_id with its compiled binary's file_id before dispatching to the agent
    async def create_go_tasking(self, taskData: PTTaskMessageAllData) -> PTTaskCreateTaskingMessageResponse:
        import os, shutil, subprocess, tempfile
        response = PTTaskCreateTaskingMessageResponse(TaskID=taskData.Task.ID, Success=True)
        file_ids = taskData.args.get_arg("files") or []
        if isinstance(file_ids, str):
            file_ids = [file_ids]

        compiled_ids = []
        for i, file_id in enumerate(file_ids, start=1):
            file_resp = await SendMythicRPCFileGetContent(MythicRPCFileGetContentMessage(AgentFileId=file_id))
            if not file_resp.Success:
                response.Success = False
                response.Error = f"failed to fetch script {i}: {file_resp.Error}"
                return response

            build_dir = tempfile.mkdtemp()
            try:
                script_path = os.path.join(build_dir, "script.py")
                with open(script_path, "wb") as fh:
                    fh.write(file_resp.Content)

                dist_dir = os.path.join(build_dir, "dist")
                result = subprocess.run(
                    [
                        "pyinstaller", "--onefile",
                        "--distpath", dist_dir,
                        "--workpath", os.path.join(build_dir, "work"),
                        "--specpath", os.path.join(build_dir, "spec"),
                        "script.py",
                    ],
                    cwd=build_dir,
                    capture_output=True,
                    text=True,
                )

                if result.returncode != 0:
                    response.Success = False
                    response.Error = f"PyInstaller failed on script {i}:\n{result.stderr}"
                    return response

                with open(os.path.join(dist_dir, "script"), "rb") as fh:
                    binary = fh.read()

                create_resp = await SendMythicRPCFileCreate(MythicRPCFileCreateMessage(
                    TaskID=taskData.Task.ID,
                    FileContents=binary,
                    DeleteAfterFetch=True,
                ))
                if not create_resp.Success:
                    response.Success = False
                    response.Error = f"failed to register binary {i}: {create_resp.Error}"
                    return response

                compiled_ids.append(create_resp.AgentFileId)
            finally:
                shutil.rmtree(build_dir, ignore_errors=True)

        taskData.args.set_arg("files", compiled_ids)
        count = len(compiled_ids)
        response.DisplayParams = f"{count} script{'s' if count != 1 else ''} (compiled)"
        return response

    # No structured output to parse — plain text response handled by Mythic automatically
    async def process_response(self, task: PTTaskMessageAllData, response: any) -> PTTaskProcessResponseMessageResponse:
        return PTTaskProcessResponseMessageResponse(TaskID=task.Task.ID, Success=True)
