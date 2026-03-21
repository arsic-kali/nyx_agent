from mythic_container.PayloadBuilder import *
from mythic_container.MythicCommandBase import *
from mythic_container.MythicRPC import *
import asyncio, os, json, tempfile, shutil, subprocess

# Defines the NyxLinuxAgent class which inherits from PayloadType and implements the build() method to compile the agent code into a binary using PyInstaller, including string substitutions for C2 profile parameters and build parameters, and returns the compiled binary as the payload to Mythic. Also defines the COMMANDS registry linking Mythic command names to their handler functions in the agent code.
class NyxLinuxAgent(PayloadType):
    name = "nyx_linux_agent"
    file_extension = ""          # binary output has no extension
    author = "arsic"
    supported_os = [SupportedOS.Linux]
    wrapper = False
    wrapped_payloads = []
    note = "Simple Linux Python callback agent"
    supports_dynamic_loading = False
    build_parameters = []
    c2_profiles = ["http"]
    mythic_encrypts = False
    translation_container = None
    agent_type = "agent"
    agent_path = Path(".") / "nyx_linux_agent" / "agent_code"
    agent_code_path = Path(".") / "nyx_linux_agent" / "agent_code"
    agent_icon_path = Path(".") / "nyx_linux_agent" / "agent_functions" / "nyx_icon.svg"

    async def build(self) -> BuildResponse:
        resp = BuildResponse(status=BuildStatus.Success)
        build_dir = None
        try:
            # 1. Load agent.py template and perform string substitutions
            agent_code_path = Path(".") / "nyx_linux_agent" / "agent_code" / "agent.py"
            with open(agent_code_path, "r") as f:
                agent_code = f.read()

            c2_profile = self.c2info[0]
            profile_params = c2_profile.get_parameters_dict()
            callback_host = profile_params.get("callback_host", "http://127.0.0.1")
            callback_port = profile_params.get("callback_port", 80)
            # Read sleep/jitter from the HTTP C2 profile so the operator
            # configures everything in one place — the listener settings
            callback_interval = profile_params.get("callback_interval", 5)
            jitter = profile_params.get("callback_jitter", 10)
            uuid = self.uuid

            agent_code = agent_code.replace("REPLACE_CALLBACK_HOST", str(callback_host))
            agent_code = agent_code.replace("REPLACE_CALLBACK_PORT", str(callback_port))
            agent_code = agent_code.replace("REPLACE_SLEEP_INTERVAL", str(callback_interval))
            agent_code = agent_code.replace("REPLACE_JITTER", str(jitter))
            agent_code = agent_code.replace("REPLACE_UUID", str(uuid))

            # 2. Write modified agent.py and commands/ package to a temp build directory
            build_dir = tempfile.mkdtemp()
            with open(os.path.join(build_dir, "agent.py"), "w") as f:
                f.write(agent_code)

            # Copy the commands/ package so PyInstaller can bundle it with the binary
            shutil.copytree(
                Path(".") / "nyx_linux_agent" / "agent_code" / "commands",
                os.path.join(build_dir, "commands")
            )

            # 3. Run PyInstaller to produce a single self-contained binary
            dist_dir = os.path.join(build_dir, "dist")
            result = subprocess.run(
                [
                    "pyinstaller", "--onefile",
                    "--distpath", dist_dir,
                    "--workpath", os.path.join(build_dir, "work"),
                    "--specpath", os.path.join(build_dir, "spec"),
                    "agent.py"
                ],
                cwd=build_dir,
                capture_output=True,
                text=True
            )
            # Surface PyInstaller output in the Mythic build log
            resp.build_stdout = result.stdout
            resp.build_stderr = result.stderr

            if result.returncode != 0:
                raise Exception(f"PyInstaller failed — see StdErr above")

            # 4. Read the compiled binary and return it as the payload
            binary_path = os.path.join(dist_dir, "agent")
            with open(binary_path, "rb") as f:
                resp.payload = f.read()

            resp.status = BuildStatus.Success
            resp.message = "Agent built successfully"

        except Exception as e:
            resp.status = BuildStatus.Error
            resp.message = f"Build failed: {str(e)}"
        finally:
            # Always clean up the temp build directory
            if build_dir:
                shutil.rmtree(build_dir, ignore_errors=True)
        return resp
