# Phase 5: Tools

## Goal
Agent can read/write files and run commands.

## What Was Built

### Files Created/Modified
- `packages/core/src/lsimons_agent/tools.py` - Tool implementations and definitions
- `packages/core/src/lsimons_agent/agent.py` - Updated to execute tools in a loop

### Tools Implemented
- `read_file(path)` - Read file contents
- `write_file(path, content)` - Write file, create parent dirs
- `edit_file(path, old_string, new_string)` - Replace unique string in file
- `bash(command)` - Execute shell command with 30s timeout

### Agent Loop Changes
- Pass TOOLS to LLM calls
- Parse tool_calls from response
- Execute tools and return results
- Loop until no more tool calls
- Added `!command` for direct bash execution

## Testing
```bash
# Terminal 1: Start mock server
uv run mock-llm-server

# Terminal 2: Run CLI with hello world scenario
echo "hello world" | uv run lsimons-agent
# Agent: I'll create a hello world Python script for you.
# [Tool: write_file(path='hello.py', content="print('Hello, World!')")]
# Agent: I've created hello.py. Let me run it to verify it works.
# [Tool: bash(command='python hello.py')]
# Agent: Done! The script works correctly and outputs 'Hello, World!'

# Test direct bash (need set +H to disable shell history expansion)
set +H; echo '!ls' | uv run lsimons-agent
# You: CLAUDE.md docs hello.py packages pyproject.toml ...
```

## Commit
`[pending]`
