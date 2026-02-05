# Agent Instructions for lsimons-agent

Custom CLI coding agent for @lsimons and @lsimons-bot. Hello-world style implementation optimized for readability.

## Quick Reference

**Python (core):**
- **Setup**: `uv sync`
- **Run CLI**: `uv run lsimons-agent`
- **Run Web**: `uv run lsimons-agent-web`
- **Run Mock LLM**: `uv run mock-llm-server`
- **Lint**: `uv run ruff check .`
- **Format**: `uv run ruff format .`
- **Test**: `uv run pytest`

**JavaScript (electron, e2e):**
- **Setup**: `pnpm install` (in package dir)
- **Lint**: `pnpm run lint`
- **Format**: `pnpm run prettier`
- **Test**: `pnpm run test`

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
   uv run ruff check . && uv run ruff format --check .
   uv run pytest
   ```

2. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

Never stop before pushing. If push fails, resolve and retry.
