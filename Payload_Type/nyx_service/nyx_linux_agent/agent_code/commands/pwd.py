import os

# Returns the agent's current working directory using os.getcwd() — no shell needed
def execute(params, task_id, callback_id):
    return os.getcwd()