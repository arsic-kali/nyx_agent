import os

def execute(params, task_id, callback_id):
    return "\n".join(f"{k}={v}" for k, v in os.environ.items())
