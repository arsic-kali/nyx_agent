import os


# Reads and returns file contents. expanduser handles ~ paths; errors="replace" prevents
# crashes on non-UTF-8 bytes by substituting ? for undecodable characters.
def execute(params, task_id, callback_id):
    path = params.strip()
    if not path:
        return "cat: no path provided"
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        return f"cat: {path}: no such file or directory"
    if os.path.isdir(path):
        return f"cat: {path}: is a directory"
    try:
        with open(path, "r", errors="replace") as fh:
            return fh.read()
    except PermissionError:
        return f"cat: {path}: permission denied"
    except Exception as e:
        return f"cat error: {str(e)}"
