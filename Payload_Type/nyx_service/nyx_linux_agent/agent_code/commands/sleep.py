from commands import config

def execute(params, task_id, callback_id):
    config.sleep_interval = float(params)
    return f"Sleep interval updated to {config.sleep_interval}s"
