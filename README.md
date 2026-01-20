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
│   │           ├── agent.py        # Main agent loop
│   │           ├── tools.py        # Tool definitions (read, write, edit, bash)
│   │           └── llm.py          # LLM client (OpenAI-compatible API)
│   ├── web/               # FastAPI backend + HTMX frontend
│   │   ├── pyproject.toml
│   │   └── src/
│   │       └── lsimons_agent_web/
│   │           ├── __init__.py
│   │           ├── server.py       # FastAPI app
│   │           ├── routes.py       # API routes
│   │           └── templates/      # Jinja2 + HTMX templates
│   └── electron/          # Electron wrapper
│       ├── package.json
│       └── main.js
├── tests/                 # Simple unit tests
├── pyproject.toml         # Root project config (uv workspace)
└── README.md
```

## Development Setup

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment and install dependencies
uv sync

# Run the CLI
uv run lsimons-agent

# Run the web server
uv run lsimons-agent-web

# Run tests
uv run pytest
```

## Environment Variables

Get `LLM_AUTH_TOKEN` from 1password:

```bash
LLM_AUTH_TOKEN=sk-...          # From 1password
LLM_BASE_URL=https://litellm.sbp.ai
LLM_DEFAULT_MODEL=azure/gpt-5-1
LLM_SMALL_FAST_MODEL=azure/gpt-5-mini
```

## Tech Stack

* **Python 3.12+** - Main language
* **uv** - Package management and virtual environments
* **FastAPI** - Web framework for the API
* **Jinja2 + HTMX** - Server-side rendering with dynamic updates
* **Electron** - Desktop app wrapper
* **pytest** - Testing (no mocking frameworks)

## Design Principles

1. **Readable code over clever code** - Favor explicit, simple implementations
2. **Minimal dependencies** - Only add what's truly needed
3. **No abstractions until needed** - Start concrete, abstract later if patterns emerge
4. **Synchronous by default** - Async adds complexity, avoid unless necessary
5. **Fail fast** - Simple error handling, let exceptions propagate

## Documentation

* [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - Phased build approach
* [Specifications](docs/SPECS.md) - Detailed feature specs for CLI, tools, web, and electron
