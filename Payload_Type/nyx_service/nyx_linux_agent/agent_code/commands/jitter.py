from commands import config

def execute(params, task_id, callback_id):
    config.jitter = float(params)
    return f"Jitter updated to {config.jitter}%"
