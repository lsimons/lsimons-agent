# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A custom CLI coding agent for @lsimons and @lsimons-bot. Hello-world style implementation optimized for readability over production use.

## Development Commands

```bash
uv sync                    # Install dependencies
uv run lsimons-agent       # Run CLI
uv run lsimons-agent-web   # Run web server
uv run pytest              # Run all tests
uv run pytest tests/test_foo.py::test_bar  # Run single test
```

## Architecture

Monorepo with uv workspaces:
- `packages/core/` - Agent logic, CLI, tools, LLM client
- `packages/web/` - FastAPI server with Jinja2+HTMX templates
- `packages/electron/` - Desktop wrapper around web UI

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
