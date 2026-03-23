import subprocess

# Runs ifconfig and returns network interface configuration
def execute(params, task_id, callback_id):
    result = subprocess.run(
        "ifconfig",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout + result.stderr
