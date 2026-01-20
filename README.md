This will be a custom CLI coding agent for use by Leo Simons (@lsimons) and his bot (@lsimons-bot).

It's inspired by stuff like
* https://ampcode.com/how-to-build-an-agent
* https://shittycodingagent.ai/
* https://rijnard.com/blog/the-code-only-agent
* https://ghuntley.com/ralph/

Things I want:

* A simple hello-world example of such a coding agent more than a daily use system.
* Optimized for readability and understandability.
* Implemented in python and using uv.
* Low on external dependencies to keep complexity down.
* Keep the python code simple and don't use advanced coding constructs.
* The CLI should also launch a simple webserver on localhost with a web UI. That should use FastAPI and HTMX. The frontend should be UX.
* Electron application that is a thin wrapper around that web frontend.
* Use vibe coding to build the coding agent.
* Experiment with the Ralph Wiggum style of vibe coding to build this, https://awesomeclaude.ai/ralph-wiggum .
* Use a monorepo setup with multiple packages (core cli, react frontend, web server, web api, frontend server, electron app, etc).
* Get any secrets from 1password.
* Simple unit tests without mocking frameworks or complex structures.

Things I don't want or need:

* MCP
* Skills
* Async
* Performance
* Image support
* Themes (just dark mode is fine)
* Configurability (just load some env vars, hardcode the rest in python)

## Project Structure

```
lsimons-agent/
├── packages/
│   ├── core/              # Core agent logic (python)
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lsimons_agent/
│   │           ├── __init__.py
│   │           ├── cli.py          # CLI entry point
│   │           ├── agent.py        # Main agent loop + process_message()
│   │           ├── tools.py        # Tool definitions (read, write, edit, bash)
│   │           └── llm.py          # LLM client (OpenAI-compatible API)
│   ├── web/               # FastAPI backend + HTMX frontend
│   │   ├── pyproject.toml
│   │   ├── src/
│   │   │   └── lsimons_agent_web/
│   │   │       ├── __init__.py
│   │   │       └── server.py       # FastAPI app (uses core agent)
│   │   └── templates/             # Jinja2 + HTMX templates
│   │       ├── base.html
│   │       └── index.html
│   ├── mock-llm/          # Mock LLM server for testing
│   │   ├── pyproject.toml
│   │   ├── scenarios.json # Canned responses
│   │   └── src/
│   │       └── mock_llm/
│   │           └── server.py
│   ├── electron/          # Electron wrapper
│   │   ├── package.json
│   │   └── main.js
│   └── e2e-tests/         # Playwright end-to-end tests
│       ├── package.json
│       ├── playwright.config.js
│       └── tests/
│           ├── chat.spec.js      # Web UI tests
│           └── electron.spec.js  # Electron app tests
├── tests/                 # Python unit tests
├── pyproject.toml         # Root project config (uv workspace)
└── README.md
```

## Development Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync --all-packages

# Run the CLI
uv run lsimons-agent

# Run the web server
uv run lsimons-agent-web

# Run mock LLM server (for testing)
uv run mock-llm-server

# Run Python tests
uv run pytest
```

## Playwright E2E Tests

The e2e tests use Playwright to test the full stack:
- `chat.spec.js` - Tests the web UI against mock server
- `electron.spec.js` - Tests the Electron app (launches electron, which starts web server)

```bash
# Install Playwright and dependencies
cd packages/e2e-tests
npm install
npx playwright install

# Run web UI tests (auto-starts mock-llm and web servers)
npm run test:web

# Run Electron tests (requires electron package to be set up)
cd ../electron && npm install && cd ../e2e-tests
npm run test:electron

# Run all tests
npm test

# Run tests in headed mode (see the browser)
npm run test:headed
```

### Test Flow

```
Playwright → Electron → Web Server → Core Agent → Mock LLM
     ↓          ↓           ↓            ↓           ↓
  browser    desktop     FastAPI    process_message  canned
  tests       app         SSE        + tools       responses
```

## Environment Variables

Get `LLM_AUTH_TOKEN` from 1password:

```bash
LLM_AUTH_TOKEN=sk-...          # From 1password
LLM_BASE_URL=https://litellm.sbp.ai
LLM_DEFAULT_MODEL=azure/gpt-5-1
LLM_SMALL_FAST_MODEL=azure/gpt-5-mini
```

For testing, leave these unset to use defaults (mock server on localhost:8000).

## Tech Stack

* **Python 3.12+** - Main language
* **uv** - Package management and virtual environments
* **FastAPI** - Web framework for the API
* **Jinja2 + HTMX** - Server-side rendering with dynamic updates
* **Electron** - Desktop app wrapper
* **Playwright** - End-to-end testing
* **pytest** - Python unit testing (no mocking frameworks)

## Design Principles

1. **Readable code over clever code** - Favor explicit, simple implementations
2. **Minimal dependencies** - Only add what's truly needed
3. **No abstractions until needed** - Start concrete, abstract later if patterns emerge
4. **Synchronous by default** - Async adds complexity, avoid unless necessary
5. **Fail fast** - Simple error handling, let exceptions propagate

## Linting

Use ruff for linting and formatting:

```bash
uv run ruff check .          # Check for errors
uv run ruff check . --fix    # Auto-fix errors
uv run ruff format .         # Format code
```

Run linting before committing. All code must pass `ruff check` with no errors.

## Testing

```bash
uv run pytest                # Run all tests
uv run pytest tests/test_tools.py  # Run one file
uv run pytest -k "test_read"       # Run tests matching name
```

Rules:
- Write tests for new functions
- Tests go in `tests/` directory
- Name test files `test_*.py`
- Name test functions `test_*`
- No mocking - use real implementations or the mock LLM server
- Keep tests simple: setup, action, assert

## Git Workflow

1. Work on `main` branch (no feature branches for this project)
2. Make small, focused commits
3. Run `uv run ruff check .` before committing
4. Run `uv run pytest` before committing
5. Write clear commit messages: what changed and why

Commit message format:
```
Short summary (50 chars or less)

Optional longer description if needed.
```

## Documentation

* [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - Phased build approach
* [Specifications](docs/SPECS.md) - Detailed feature specs for CLI, tools, web, and electron
