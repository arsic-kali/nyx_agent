import subprocess

# Runs ss -tulpn and returns listening/established TCP and UDP sockets with process info
def execute(params, task_id, callback_id):
    result = subprocess.run(
        "ss -tulpn",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout + result.stderr
