import subprocess

# Runs netstat -antlp and returns all TCP connections with process info
def execute(params, task_id, callback_id):
    result = subprocess.run(
        "netstat -antlp",
        shell=True,
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout + result.stderr
