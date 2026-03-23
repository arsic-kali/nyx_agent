# Reads and returns the contents of /etc/passwd
def execute(params, task_id, callback_id):
    try:
        with open("/etc/passwd", "r") as fh:
            return fh.read()
    except PermissionError:
        return "passwd: permission denied"
    except Exception as e:
        return f"passwd error: {str(e)}"
