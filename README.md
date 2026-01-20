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
