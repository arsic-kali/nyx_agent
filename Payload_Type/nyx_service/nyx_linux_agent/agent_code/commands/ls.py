import subprocess

# Execute ls -la from your cwd and return the output, with a timeout of 30 seconds to prevent hanging if something goes wrong. The result should include both stdout and stderr to capture any potential error messages.
def execute(params, task_id, callback_id):
    cmd = "ls -la;"
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout + result.stderr
