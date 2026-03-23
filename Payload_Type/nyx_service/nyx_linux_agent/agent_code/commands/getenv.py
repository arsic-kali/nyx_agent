import os

# Returns all environment variables as KEY=VALUE lines
def execute(params, task_id, callback_id):
    return "\n".join(f"{k}={v}" for k, v in os.environ.items())
