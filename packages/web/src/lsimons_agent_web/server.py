"""Web server for lsimons-agent."""

import json
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from lsimons_agent.llm import chat
from lsimons_agent.tools import TOOLS, execute

app = FastAPI()

# Templates directory
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# System prompt (same as CLI)
SYSTEM_PROMPT = """\
You are a coding assistant. You help the user by reading, writing, and editing \
files, and running shell commands.

When editing files, use edit_file with the exact string to replace - include \
enough context to make the match unique.

Be concise. Execute tasks directly without asking for confirmation."""

# Store conversation state (simple in-memory, single user)
messages = [{"role": "system", "content": SYSTEM_PROMPT}]


def event_stream(user_message: str):
    """Generate SSE events for a chat response."""
    global messages

    messages.append({"role": "user", "content": user_message})

    while True:
        response = chat(messages, tools=TOOLS)
        message = response["choices"][0]["message"]
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        if content:
            yield f"event: text\ndata: {json.dumps({'content': content})}\n\n"

        if not tool_calls:
            messages.append(message)
            break

        # Execute tools
        messages.append(message)
        for tool_call in tool_calls:
            fn = tool_call["function"]
            name = fn["name"]
            args = json.loads(fn["arguments"])

            yield f"event: tool\ndata: {json.dumps({'name': name, 'args': args})}\n\n"

            try:
                result = execute(name, args)
            except Exception as e:
                result = f"Error: {e}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result,
            })

    yield "event: done\ndata: {}\n\n"


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    """Serve the chat page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/chat")
def chat_endpoint(request: dict):
    """Handle chat messages and return SSE stream."""
    message = request.get("message", "")
    return StreamingResponse(
        event_stream(message),
        media_type="text/event-stream",
    )


@app.post("/clear")
def clear():
    """Clear conversation history."""
    global messages
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    return {"status": "ok"}


def main():
    """Run the web server."""
    import uvicorn

    print("Starting web server on http://localhost:8765")
    uvicorn.run(app, host="127.0.0.1", port=8765)


if __name__ == "__main__":
    main()
