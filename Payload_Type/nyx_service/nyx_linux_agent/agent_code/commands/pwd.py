import os

# Return current working directory using os.getcwd() — this is a simple command that doesn't require shell execution, so we can just call the Python function directly without invoking a shell. This also avoids potential issues with shell quoting and escaping.
def execute(params, task_id, callback_id):
    return os.getcwd()