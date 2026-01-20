# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A custom CLI coding agent for @lsimons and @lsimons-bot. Hello-world style implementation optimized for readability over production use.

## Development Commands

```bash
uv sync                    # Install dependencies
uv run lsimons-agent       # Run CLI
uv run lsimons-agent-web   # Run web server
uv run mock-llm-server     # Run mock LLM for testing
uv run ruff check .        # Lint code
uv run ruff format .       # Format code
uv run pytest              # Run all tests
```

## Before Committing

1. Run `uv run ruff check .` - fix any errors
2. Run `uv run pytest` - all tests must pass
3. Write a clear commit message (what + why)

## Architecture

Monorepo with uv workspaces:
- `packages/lsimons-agent/` - Agent logic, CLI, tools, LLM client
- `packages/lsimons-agent-web/` - FastAPI server with HTML template
- `packages/mock-llm-server/` - Mock LLM for testing
- `packages/lsimons-agent-electron/` - Desktop wrapper around web UI
- `packages/lsimons-agent-e2e-tests/` - Playwright end-to-end tests

## Code Style

- **Synchronous only** - No async/await
- **Simple Python** - Avoid advanced constructs, favor explicit code
- **Minimal dependencies** - Only add what's truly needed
- **No mocking** - Tests use real implementations
- **Fail fast** - Let exceptions propagate, simple error handling

## Environment

Get `LLM_AUTH_TOKEN` from 1password. Other env vars:
```
LLM_BASE_URL=https://litellm.sbp.ai
LLM_DEFAULT_MODEL=azure/gpt-5-1
LLM_SMALL_FAST_MODEL=azure/gpt-5-mini
```
