# Nyx — Mythic C2 Linux Agent

Nyx is a Python-based Linux agent for the [Mythic C2 framework](https://github.com/its-a-feature/Mythic). It is designed as a learning-focused, modular agent that compiles to a standalone binary using PyInstaller.

---

## Features

- Registers with Mythic via the HTTP C2 profile
- Modular command architecture — new commands are added without touching core agent logic

## Requirements

- [Mythic C2](https://github.com/its-a-feature/Mythic) installed and running
- Docker (managed by Mythic)
- The HTTP C2 profile installed in Mythic

---

## Installation

Install the agent into your Mythic instance:

```bash
cd /opt/Mythic
sudo ./mythic-cli install folder /path/to/nyx_agent/
```

Mythic will build the Docker container automatically. The container installs all dependencies including PyInstaller and binutils.

---

## Building a Payload

1. Open the Mythic UI
2. Navigate to **Payloads** → **Generate New Payload**
3. Navigate through the Payload Creation
4. Generate the Payload
5. Download the compiled binary
6. Deploy to target: `chmod +x <payload> && ./<payload>`

---

## Supported Commands

| Command  | Description |
|----------|-------------|
| `shell`  | Execute a shell command and return output |
| `ls`     | List contents of the current working directory |
| `cd`     | Change the agent's current working directory |
| `pwd`    | Print the current working directory |
| `whoami` | Print the current user |
| `getenv` | Print all environment variables |
| `sleep`  | Set the agent sleep interval in seconds |
| `jitter` | Set the agent jitter percentage |
| `download` | Download a file from the target |
| `upload`   | Upload a file to the target |
| `runpy`    | Transfer a Python script from the operator and execute it on the target |
| `campaign` | Transfer and execute multiple Python scripts in sequence, reporting each result separately |
| `exit`   | Terminate the agent and close the callback |

---

## Project Structure

```
nyx_agent/
├── config.json                          # Mythic install config
└── Payload_Type/
    └── nyx_service/
        ├── Dockerfile                   # Container definition
        ├── main.py                      # Service entrypoint — starts Mythic container runtime
        └── nyx_linux_agent/
            ├── agent_code/              # Code compiled into the payload and run on target
            │   ├── agent.py             # Core agent: checkin, tasking loop, command dispatch
            │   └── commands/            # One file per command, each exposing execute()
            └── agent_functions/         # Mythic-side definitions — run in service container
                ├── builder.py           # Payload build logic
                ├── <cmd>.py             # Mythic-side commanding logic
```

---

## Adding a New Command

Each new command requires two files:

**1. `agent_code/commands/<name>.py`** — execution logic (runs on target)
```python
def execute(params, task_id, callback_id):
    # do work, return output string
    return output
```

**2. `agent_functions/<name>.py`** — Mythic definition (runs in service container)
- Subclass `TaskArguments` to define parameters
- Subclass `CommandBase` to register with Mythic

Then register it in two places:

```python
# agent_code/agent.py
from commands import <name> as cmd_<name>

COMMANDS = {
    "shell": cmd_shell.execute,
    "<name>": cmd_<name>.execute,   # add this line
}
```

```python
# agent_functions/__init__.py
from nyx_linux_agent.agent_functions import <name>   # add this line
```

Reinstall the service after any changes:
```bash
sudo ./mythic-cli install folder /path/to/nyx_agent/
```

---

## How It Works

```
Operator issues command in Mythic UI
        ↓
agent_functions/<cmd>.py validates and queues the task
        ↓
agent.py polls /agent_message, receives task JSON
        ↓
handle_task() dispatches to commands/<cmd>.execute()
        ↓
Output sent back via post_response()
        ↓
Result appears in Mythic UI
```

All messages follow Mythic's wire format: `base64( callback_uuid + json_body )`
