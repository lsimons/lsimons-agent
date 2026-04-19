# Agent Instructions for lsimons-agent

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

Custom CLI coding agent for @lsimons and @lsimons-bot. Hello-world style implementation optimized for readability.

## Quick Reference

**One-time (any language):** `mise install`

**Python (core):**
- **Setup**: `mise run install` (or `uv sync --all-groups --all-packages`)
- **Run CLI**: `uv run lsimons-agent`
- **Run Web**: `uv run lsimons-agent-web`
- **Run Mock LLM**: `uv run mock-llm-server`
- **Lint**: `mise run lint` (ruff check + format --check)
- **Typecheck**: `mise run typecheck` (basedpyright)
- **Format**: `mise run format`
- **Test**: `mise run test` (or `uv run pytest`)
- **Full CI gate**: `mise run ci`

**JavaScript (electron, e2e):**
- **Setup**: `cd packages/<pkg> && npm install`
- **Lint / Format / Test**: use each package's own scripts

## Structure

Monorepo with uv workspaces (Python) and pnpm (JS):
- `packages/lsimons-agent/` - Agent logic, CLI, tools, LLM client (Python)
- `packages/lsimons-agent-web/` - FastAPI server with HTML template (Python)
- `packages/mock-llm-server/` - Mock LLM for testing (Python)
- `packages/lsimons-agent-electron/` - Desktop wrapper (JS/Electron)
- `packages/lsimons-agent-e2e-tests/` - Playwright tests (JS)

## Guidelines

**Python code style:**
- Synchronous only (no async/await)
- Simple, explicit Python
- Minimal dependencies
- No mocking in tests (use real implementations)
- Fail fast (let exceptions propagate)
- ruff for linting and formatting

**JavaScript code style:**
- ESLint + Prettier: zero warnings/errors
- Strict TypeScript where applicable
- Playwright for e2e testing

**Environment:** Get `LLM_AUTH_TOKEN` from 1Password.

**Specs:** Significant features need a spec in `docs/spec/`. Wait for human review before implementing.

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `revert`, `improvement`, `chore`

## Session Completion

Work is NOT complete until `git push` succeeds.

1. **Quality gates** (if code changed):
   ```bash
   mise run ci
   ```

2. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

Never stop before pushing. If push fails, resolve and retry.
