from commands import config

# Updates the shared sleep interval read by the main loop in agent.py on each iteration
def execute(params, task_id, callback_id):
    config.sleep_interval = float(params)
    return f"Sleep interval updated to {config.sleep_interval}s"
