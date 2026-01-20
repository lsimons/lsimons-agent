# Phase 6: Web Interface

## Goal
Browser-based chat UI.

## What Was Built

### Files Created
- `packages/web/pyproject.toml` - Package config with FastAPI, Jinja2 deps
- `packages/web/src/lsimons_agent_web/__init__.py` - Package init
- `packages/web/src/lsimons_agent_web/server.py` - FastAPI web server
- `packages/web/templates/base.html` - Base template with dark theme styles
- `packages/web/templates/index.html` - Chat interface with HTMX

### Endpoints
- `GET /` - Serves chat page
- `POST /chat` - Returns SSE stream with events: text, tool, done
- `POST /clear` - Resets conversation history

### Features
- Dark mode UI with monospace font
- SSE streaming for real-time responses
- Tool execution display
- Clear button to reset conversation
- Uses same agent logic as CLI

## Testing
```bash
# Terminal 1: Start mock server
uv run mock-llm-server

# Terminal 2: Start web server
uv run lsimons-agent-web

# Terminal 3: Test with curl
curl -s http://localhost:8765/
# Returns HTML page

curl -s -X POST http://localhost:8765/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"how are you"}'
# event: text
# data: {"content": "I'm doing well, thank you for asking!"}
# event: done
# data: {}
```

## Commit
`[pending]`
