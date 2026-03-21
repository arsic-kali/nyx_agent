import os

def execute(params, task_id, callback_id):
    try:
        os.chdir(params.strip())
        return os.getcwd()
    except Exception as e:
        return f"cd failed: {str(e)}"
