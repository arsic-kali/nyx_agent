import os
import json

def execute(params, task_id, callback_id):
    try:
        path = json.loads(params).get("path", "")
    except Exception:
        path = params

    try:
        os.chdir(path.strip())
        return os.getcwd()
    except Exception as e:
        return f"cd failed: {str(e)}"
