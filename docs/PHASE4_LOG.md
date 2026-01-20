# Phase 4: Conversation Loop

## Goal
Interactive REPL with multi-turn conversation.

## What Was Built

### Files Created/Modified
- `packages/core/src/lsimons_agent/agent.py` - Agent loop with REPL
- `packages/core/src/lsimons_agent/cli.py` - Simplified to call agent

### Agent Loop
The `run()` function:
- Maintains messages list with system prompt
- Reads user input in a loop
- Handles `/clear` to reset conversation
- Handles Ctrl+C and EOF to exit
- Calls LLM and prints response

### Commands
- Type message + Enter: Send to agent
- Empty line: Ignored
- `/clear`: Reset conversation (keeps system prompt)
- Ctrl+C: Exit

## Testing
```bash
# Terminal 1: Start mock server
uv run mock-llm-server

# Terminal 2: Run CLI
uv run lsimons-agent
# You: how are you
# Agent: I'm doing well, thank you for asking!
# You: /clear
# Cleared.
# You: how are you
# Agent: I'm doing well, thank you for asking!
# Ctrl+C
# Bye!
```

## Commit
`[pending]`
