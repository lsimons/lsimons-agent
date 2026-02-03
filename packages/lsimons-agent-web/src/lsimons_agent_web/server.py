"""Web server for lsimons-agent."""

import json
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
from lsimons_agent.agent import new_conversation, process_message

app = FastAPI()


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


@app.get("/", response_class=HTMLResponse)
def index():
    """Serve the chat page."""
    return (TEMPLATES_DIR / "index.html").read_text()


@app.get("/favicon.ico")
def favicon():
    """Serve the favicon."""
    return FileResponse(STATIC_DIR / "favicon.ico", media_type="image/x-icon")


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


def main():
    """Run the web server."""
    import uvicorn

    print("Starting web server on http://localhost:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765)


if __name__ == "__main__":
    main()
