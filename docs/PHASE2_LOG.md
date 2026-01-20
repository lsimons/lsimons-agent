# Phase 2: Mock LLM Server

## Goal
Create a predictable test server that mimics the LiteLLM API with canned responses.

## What Was Built

### Files Created
- `packages/mock-llm/pyproject.toml` - Package config with FastAPI/uvicorn deps
- `packages/mock-llm/src/mock_llm/__init__.py` - Package init
- `packages/mock-llm/src/mock_llm/server.py` - FastAPI server
- `packages/mock-llm/scenarios.json` - Canned responses

### Server Endpoints
- `POST /chat/completions` - OpenAI-compatible chat endpoint
- `GET /health` - Health check

### Scenario Matching
The server matches incoming messages against triggers in scenarios.json:
1. Extract last user message
2. Find scenario where `trigger` is substring of message
3. Return corresponding response (with optional tool_calls)
4. Track state for multi-step scenarios

### Scenarios Included
- `hello-world` - Creates and runs hello.py (3 steps with tool calls)
- `simple-chat` - Simple "how are you" response (1 step)

## Testing
```bash
uv run mock-llm-server &
curl -X POST http://localhost:8000/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"test","messages":[{"role":"user","content":"hello world"}]}'
# Returns response with write_file tool call
```

## Issues Encountered
None. FastAPI and Pydantic worked out of the box.

## Commit
`a697d6d` - Phase 2: Mock LLM Server
