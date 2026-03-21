import os
import pwd

# Gets current user and returns it
def execute(params, task_id, callback_id):
    return pwd.getpwuid(os.getuid()).pw_name

