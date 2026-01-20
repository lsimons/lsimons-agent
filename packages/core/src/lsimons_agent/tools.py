"""Tools for the coding agent."""

import subprocess
from pathlib import Path

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"},
                },
                "required": ["path", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing a specific string with another",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to edit"},
                    "old_string": {
                        "type": "string",
                        "description": "Exact string to find and replace",
                    },
                    "new_string": {"type": "string", "description": "String to replace with"},
                },
                "required": ["path", "old_string", "new_string"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"}
                },
                "required": ["command"],
            },
        },
    },
]


def read_file(path: str) -> str:
    """Read and return file contents."""
    return Path(path).read_text()


def write_file(path: str, content: str) -> str:
    """Write content to file. Creates parent dirs if needed."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content)
    return "OK"


def edit_file(path: str, old_string: str, new_string: str) -> str:
    """Replace old_string with new_string in file."""
    p = Path(path)
    content = p.read_text()
    count = content.count(old_string)
    if count == 0:
        raise ValueError(f"String not found in {path}")
    if count > 1:
        raise ValueError(f"String appears {count} times in {path}, must be unique")
    p.write_text(content.replace(old_string, new_string))
    return "OK"


def bash(command: str) -> str:
    """Execute shell command and return combined stdout+stderr."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout + result.stderr
        if result.returncode != 0:
            output += f"\n[exit code: {result.returncode}]"
        return output.strip() or "(no output)"
    except subprocess.TimeoutExpired:
        return "[timed out after 30s]"


def execute(name: str, args: dict) -> str:
    """Execute a tool by name and return the result."""
    if name == "read_file":
        return read_file(**args)
    elif name == "write_file":
        return write_file(**args)
    elif name == "edit_file":
        return edit_file(**args)
    elif name == "bash":
        return bash(**args)
    else:
        return f"Unknown tool: {name}"
