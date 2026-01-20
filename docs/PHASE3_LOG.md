# Phase 3: Single LLM Call

## Goal
CLI sends one hardcoded message to LLM and prints the response.

## What Was Built

### Files Created/Modified
- `packages/core/src/lsimons_agent/llm.py` - LLM client with `chat()` function
- `packages/core/src/lsimons_agent/cli.py` - Updated to call LLM
- `packages/core/pyproject.toml` - Added httpx dependency

### LLM Client
The `chat()` function:
- Uses httpx for HTTP requests
- Reads config from environment variables with sensible defaults
- Defaults to `http://localhost:8000` (mock server)
- Returns raw OpenAI-format response dict

### Environment Variables
```
LLM_BASE_URL    - API endpoint (default: http://localhost:8000)
LLM_AUTH_TOKEN  - Bearer token (default: empty)
LLM_DEFAULT_MODEL - Model name (default: mock-model)
```

## Testing
```bash
# Terminal 1: Start mock server
uv run mock-llm-server

# Terminal 2: Run CLI
uv run lsimons-agent
# Output:
# lsimons-agent
# ----------------------------------------
# You: how are you
#
# Agent: I'm doing well, thank you for asking!
```

## Issues Encountered
None. httpx client worked cleanly with the mock server.

## Commit
`e757840` - Phase 3: Single LLM Call
