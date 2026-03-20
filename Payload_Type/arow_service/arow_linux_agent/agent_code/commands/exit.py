import sys


# Called by handle_task() when Mythic sends a task with command="exit".
# Posts the goodbye response first via handle_task, then terminates the process.
# Returns a string like all other commands — handle_task calls post_response
# before calling sys.exit(0) directly after.
def execute(params, task_id, callback_id):
    return "Agent exiting."
