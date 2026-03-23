import subprocess

# Runs the route command and returns the kernel routing table
def execute(params, task_id, callback_id):
    cmd = "route"
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout + result.stderr