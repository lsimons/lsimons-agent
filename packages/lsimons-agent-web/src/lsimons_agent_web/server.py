"""Web server for lsimons-agent."""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from lsimons_agent.agent import new_conversation, process_message

from .terminal import Terminal

app = FastAPI()

# Terminal sessions keyed by (project_path, terminal_type, agent)
# e.g., ("/Users/foo/git/org/repo", "agent", "claude") or ("...", "shell", None)
terminals: dict[tuple[str, str, str | None], Terminal] = {}

# Agent command mapping
AGENT_COMMANDS = {
    "lsimons": ["lsimons-agent-client"],
    "claude": ["claude"],
    "pi": ["pi"],
    "gemini": ["gemini"],
    "github": ["gh", "copilot"],
}

# Git base directory
GIT_BASE_DIR = Path.home() / "git"


def get_resource_path(relative_path: str) -> Path:
    """Get path to resource, handling PyInstaller bundled mode."""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        # Running in PyInstaller bundle
        return Path(sys._MEIPASS) / relative_path
    # Running in normal Python environment
    return Path(__file__).parent.parent.parent / relative_path


TEMPLATES_DIR = get_resource_path("templates")
STATIC_DIR = get_resource_path("static")

# Single-user conversation state
messages = new_conversation()


def event_stream(user_message: str):
    """Generate SSE events for a chat response."""
    for event_type, data in process_message(messages, user_message):
        if event_type == "text":
            yield f"event: text\ndata: {json.dumps({'content': data})}\n\n"
        elif event_type == "tool":
            yield f"event: tool\ndata: {json.dumps(data)}\n\n"
        elif event_type == "done":
            yield "event: done\ndata: {}\n\n"


def scan_git_repos() -> dict[str, list[str]]:
    """Scan ~/git for git repositories, organized by org."""
    repos: dict[str, list[str]] = {}

    if not GIT_BASE_DIR.exists():
        return repos

    for org_dir in sorted(GIT_BASE_DIR.iterdir()):
        if not org_dir.is_dir() or org_dir.name.startswith("."):
            continue

        org_repos = []
        for repo_dir in sorted(org_dir.iterdir()):
            if not repo_dir.is_dir() or repo_dir.name.startswith("."):
                continue
            # Check if it's a git repo
            if (repo_dir / ".git").exists():
                org_repos.append(repo_dir.name)

        if org_repos:
            repos[org_dir.name] = org_repos

    return repos


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the terminal page."""
    return (TEMPLATES_DIR / "terminal.html").read_text()


@app.get("/favicon.ico")
def favicon():
    """Serve the favicon."""
    return FileResponse(STATIC_DIR / "favicon.ico", media_type="image/x-icon")


@app.get("/logo.png")
def logo():
    """Serve the logo."""
    return FileResponse(STATIC_DIR / "logo.png", media_type="image/png")


@app.post("/chat")
def chat_endpoint(request: dict):
    """Handle chat messages and return SSE stream."""
    return StreamingResponse(
        event_stream(request.get("message", "")),
        media_type="text/event-stream",
    )


@app.post("/clear")
def clear():
    """Clear conversation history."""
    global messages
    messages = new_conversation()
    return {"status": "ok"}


@app.get("/api/repos")
def list_repos():
    """List available git repositories."""
    return scan_git_repos()


@app.post("/api/sync")
def sync_repos():
    """Run auto git-sync and return updated repo list."""
    try:
        subprocess.run(["auto", "git-sync"], check=True, capture_output=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass  # Ignore errors, still return repo list
    return scan_git_repos()


async def _handle_terminal_websocket(
    websocket: WebSocket, terminal: Terminal
) -> None:
    """Handle WebSocket I/O for a terminal."""
    try:
        while True:
            # Check if terminal is still running
            if not terminal.is_running():
                break

            # Poll for terminal output
            while True:
                data = terminal.read_nowait()
                if data is None:
                    break
                try:
                    await websocket.send_bytes(data)
                except RuntimeError:
                    # WebSocket already closed
                    return

            # Check for websocket input (with timeout)
            try:
                message = await asyncio.wait_for(
                    websocket.receive(), timeout=0.05
                )
                if message.get("type") == "websocket.disconnect":
                    break
                if "bytes" in message:
                    terminal.write(message["bytes"])
                elif "text" in message:
                    # Handle JSON commands (resize)
                    try:
                        cmd = json.loads(message["text"])
                        if cmd.get("type") == "resize":
                            terminal.resize(cmd["rows"], cmd["cols"])
                    except json.JSONDecodeError:
                        # Plain text input
                        terminal.write(message["text"].encode())
            except asyncio.TimeoutError:
                pass

    except (WebSocketDisconnect, RuntimeError):
        # WebSocket disconnected
        pass


def get_project_path(project: str | None) -> str:
    """Get the full path for a project, or cwd if None."""
    if not project:
        return os.getcwd()

    # Project format: "org/repo"
    if "/" in project:
        return str(GIT_BASE_DIR / project)

    return os.getcwd()


@app.websocket("/ws/terminal/agent")
async def terminal_agent_websocket(
    websocket: WebSocket, agent: str = "lsimons", project: str | None = None
):
    """WebSocket endpoint for agent terminal."""
    global terminals

    await websocket.accept()

    # Validate agent type
    if agent not in AGENT_COMMANDS:
        agent = "lsimons"

    project_path = get_project_path(project)
    key = (project_path, "agent", agent)

    # Clean up dead terminal
    if key in terminals and not terminals[key].is_running():
        terminals[key].stop()
        del terminals[key]

    # Start new terminal or reconnect to existing
    if key not in terminals:
        terminal = Terminal(command=AGENT_COMMANDS[agent], cwd=project_path)
        terminal.start()
        terminals[key] = terminal
    else:
        # Reconnecting - replay scrollback buffer
        scrollback = terminals[key].get_scrollback()
        if scrollback:
            await websocket.send_bytes(scrollback)

    await _handle_terminal_websocket(websocket, terminals[key])


@app.websocket("/ws/terminal/shell")
async def terminal_shell_websocket(
    websocket: WebSocket, project: str | None = None
):
    """WebSocket endpoint for shell terminal."""
    global terminals

    await websocket.accept()

    project_path = get_project_path(project)
    key = (project_path, "shell", None)

    # Clean up dead terminal
    if key in terminals and not terminals[key].is_running():
        terminals[key].stop()
        del terminals[key]

    # Start new terminal or reconnect to existing
    if key not in terminals:
        terminal = Terminal(cwd=project_path)
        terminal.start()
        terminals[key] = terminal
    else:
        # Reconnecting - replay scrollback buffer
        scrollback = terminals[key].get_scrollback()
        if scrollback:
            await websocket.send_bytes(scrollback)

    await _handle_terminal_websocket(websocket, terminals[key])


@app.post("/terminal/stop")
def terminal_stop():
    """Stop all terminal sessions."""
    global terminals
    for terminal in terminals.values():
        terminal.stop()
    terminals.clear()
    return {"status": "ok"}


def main():
    """Run the web server."""
    import uvicorn

    print("Starting web server on http://localhost:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765)


if __name__ == "__main__":
    main()
