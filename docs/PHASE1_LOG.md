# Phase 1: Hello World CLI

## Goal
Create a runnable CLI that prints a message.

## What Was Built

### Files Created
- `pyproject.toml` - Root workspace config for uv
- `packages/core/pyproject.toml` - Core package with CLI entry point
- `packages/core/src/lsimons_agent/__init__.py` - Package init
- `packages/core/src/lsimons_agent/cli.py` - CLI that prints hello
- `.gitignore` - Ignore Python, uv, IDE, and OS files

### Key Decisions
- Used uv workspaces with `[tool.uv.workspace]` pointing to `packages/*`
- Used hatchling as the build backend (simpler than setuptools)
- CLI entry point defined in `[project.scripts]`

## Testing
```bash
uv sync
uv run lsimons-agent
# Output: Hello from lsimons-agent!
```

## Issues Encountered
- uv was not installed, had to run install script
- After `uv sync`, packages were not installed in editable mode
- Fixed by running `uv pip install -e packages/core`

## Commit
`b7d1cf1` - Phase 1: Hello World CLI
