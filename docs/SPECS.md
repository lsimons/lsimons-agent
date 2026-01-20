# Feature Specifications

## Design Philosophy

Inspired by:
- [ampcode](https://ampcode.com/how-to-build-an-agent) - "An LLM, a loop, and sufficient tokens." ~300 lines total.
- [shittycodingagent](https://shittycodingagent.ai/) - 4 tools (read, write, edit, bash). Avoid MCP, sub-agents, planning modes.
- [code-only-agent](https://rijnard.com/blog/the-code-only-agent) - Code as witness. Deterministic execution.
- [ralph](https://ghuntley.com/ralph/) - Iterative refinement through prompt tuning. Embrace "deterministically bad" outputs.

Core principle: Keep it simple. When the agent does something wrong, improve the prompt, not the architecture.

---

## CLI Interface

### Invocation
```bash
uv run lsimons-agent      # CLI only
uv run lsimons-agent-web  # Web server on localhost:8765
```

### Behavior
- `lsimons-agent`: Start interactive REPL mode
- `lsimons-agent-web`: Start web server with chat UI

### REPL Commands
- Type message + Enter: Send to agent
- Empty line: Ignored
- Ctrl+C: Exit
- `/clear`: Reset conversation history
- `!command`: Execute bash directly (bypass LLM)

### Output Format
```
You: <user message>

Agent: <response text>

[Tool: read_file("src/main.py")]
[Tool: edit_file("src/main.py", ...)]

Agent: <continued response>

You: _
```

---

## LLM Client

Uses OpenAI-compatible API via LiteLLM proxy.

### Function Signature
```python
def chat(
    messages: list[dict],
    tools: list[dict] | None = None,
    model: str | None = None
) -> dict:
    """
    Send messages to LLM and return the response.

    Args:
        messages: List of {"role": "system"|"user"|"assistant", "content": ...}
        tools: Optional tool definitions (OpenAI format)
        model: Override default model

    Returns:
        Raw API response dict (OpenAI chat completion format)

    Raises:
        Exception on API errors (no retry logic)
    """
```

### Configuration (Environment Variables)
```bash
LLM_AUTH_TOKEN=sk-...        # From 1password
LLM_BASE_URL=https://litellm.sbp.ai
LLM_DEFAULT_MODEL=azure/gpt-5-1
LLM_SMALL_FAST_MODEL=azure/gpt-5-mini
```

### Implementation
```python
import httpx

def chat(messages, tools=None, model=None):
    url = os.environ["LLM_BASE_URL"] + "/chat/completions"
    model = model or os.environ["LLM_DEFAULT_MODEL"]

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
    }
    if tools:
        payload["tools"] = tools

    response = httpx.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {os.environ['LLM_AUTH_TOKEN']}"},
        timeout=120.0
    )
    response.raise_for_status()
    return response.json()
```

---

## Mock LLM Server

Test server that returns canned responses. Used for development and testing without real LLM costs.

### Invocation
```bash
uv run mock-llm-server [--port 8000]
```

### Endpoint

#### POST /chat/completions

Matches incoming messages against scenarios and returns canned response.

Matching logic:
1. Extract last user message content
2. Find scenario where `trigger` is substring of user message
3. Return corresponding `response`
4. If no match, return default "I don't understand" response

### Scenarios File

`packages/mock-llm-server/scenarios.json`:
```json
{
  "scenarios": [
    {
      "name": "hello-world",
      "trigger": "hello world",
      "steps": [
        {
          "response": {
            "content": "I'll create a hello world Python script for you.",
            "tool_calls": [
              {
                "id": "call_001",
                "type": "function",
                "function": {
                  "name": "write_file",
                  "arguments": "{\"path\": \"hello.py\", \"content\": \"print('Hello, World!')\"}"
                }
              }
            ]
          }
        },
        {
          "response": {
            "content": "I've created hello.py. Let me run it to verify it works.",
            "tool_calls": [
              {
                "id": "call_002",
                "type": "function",
                "function": {
                  "name": "bash",
                  "arguments": "{\"command\": \"python hello.py\"}"
                }
              }
            ]
          }
        },
        {
          "response": {
            "content": "Done! The script works correctly and outputs 'Hello, World!'"
          }
        }
      ]
    },
    {
      "name": "simple-chat",
      "trigger": "how are you",
      "steps": [
        {
          "response": {
            "content": "I'm doing well, thank you for asking!"
          }
        }
      ]
    }
  ],
  "default_response": {
    "content": "I'm a mock server. I only understand specific test scenarios."
  }
}
```

### Response Format

Returns standard OpenAI chat completion format:
```json
{
  "id": "mock-12345",
  "object": "chat.completion",
  "model": "mock-model",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "...",
        "tool_calls": [...]
      },
      "finish_reason": "stop"
    }
  ]
}
```

### State Tracking

The mock server determines the current step by counting tool result messages:
- Each scenario has multiple `steps`
- Step index = count of `role: "tool"` messages in conversation
- No server-side state needed - purely based on message history

---

## Tools

Four tools only: read, write, edit, bash.

### read_file
```python
def read_file(path: str) -> str:
    """Read and return file contents. Raises FileNotFoundError if missing."""
```

### write_file
```python
def write_file(path: str, content: str) -> str:
    """Write content to file. Creates parent dirs if needed. Returns 'OK'."""
```

### edit_file
```python
def edit_file(path: str, old_string: str, new_string: str) -> str:
    """
    Replace old_string with new_string in file.
    Raises ValueError if old_string not found or not unique.
    Returns 'OK'.
    """
```

### bash
```python
def bash(command: str) -> str:
    """
    Execute shell command and return combined stdout+stderr.
    Times out after 30 seconds.
    Returns output even if command fails (includes exit code in output).
    """
```

### Tool Definitions (OpenAI Format)
```python
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read the contents of a file",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to read"}
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write content to a file (creates or overwrites)",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to write"},
                    "content": {"type": "string", "description": "Content to write"}
                },
                "required": ["path", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "edit_file",
            "description": "Edit a file by replacing a specific string with another",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "File path to edit"},
                    "old_string": {"type": "string", "description": "Exact string to find and replace"},
                    "new_string": {"type": "string", "description": "String to replace with"}
                },
                "required": ["path", "old_string", "new_string"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bash",
            "description": "Execute a shell command",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {"type": "string", "description": "Command to execute"}
                },
                "required": ["command"]
            }
        }
    }
]
```

---

## Agent Loop

### Pseudocode
```
messages = [{"role": "system", "content": SYSTEM_PROMPT}]

loop:
    user_input = read_line()

    if user_input.startswith("!"):
        # Direct bash execution
        print(bash(user_input[1:]))
        continue

    if user_input == "/clear":
        messages = [messages[0]]  # Keep system prompt
        continue

    messages.append({"role": "user", "content": user_input})

    loop:
        response = chat(messages, tools=TOOLS)
        choice = response["choices"][0]
        message = choice["message"]

        # Print text content
        if message.get("content"):
            print(message["content"])

        # Check for tool calls
        tool_calls = message.get("tool_calls", [])
        if not tool_calls:
            messages.append(message)
            break

        # Execute tools
        messages.append(message)
        for tool_call in tool_calls:
            fn = tool_call["function"]
            args = json.loads(fn["arguments"])
            result = execute_tool(fn["name"], args)
            print(f"[Tool: {fn['name']}(...)]")
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result
            })
```

### System Prompt
```
You are a coding assistant. You help the user by reading, writing, and editing files, and running shell commands.

When editing files, use edit_file with the exact string to replace - include enough context to make the match unique.

Be concise. Execute tasks directly without asking for confirmation.
```

---

## Web Server

### Endpoints

#### GET /
Serves the main chat page (index.html template).

#### POST /chat
Send a message and receive streamed response.

#### POST /clear
Reset conversation history. Returns `{"status": "ok"}`.

Request:
```json
{"message": "string"}
```

Response: Server-Sent Events stream
```
event: text
data: {"content": "Here's what I found..."}

event: tool
data: {"name": "read_file", "input": {"path": "foo.py"}}

event: done
data: {}
```

### Template

Single `index.html` file containing:
- Dark mode CSS styles
- Message history container
- Input form with vanilla JS fetch() to /chat
- SSE handling for streaming responses

---

## Electron App

### main.js Structure
```javascript
const { app, BrowserWindow } = require('electron');
const { spawn } = require('child_process');

let serverProcess = null;
let mainWindow = null;

function startServer() {
    serverProcess = spawn('uv', ['run', 'lsimons-agent-web'], {
        cwd: __dirname + '/..'
    });
    // Wait for server ready (poll localhost:8765)
}

function createWindow() {
    mainWindow = new BrowserWindow({
        width: 900,
        height: 700,
        webPreferences: { nodeIntegration: false }
    });
    mainWindow.loadURL('http://localhost:8765');
}

app.whenReady().then(async () => {
    await startServer();
    createWindow();
});

app.on('quit', () => {
    if (serverProcess) serverProcess.kill();
});
```

### package.json Scripts
```json
{
    "scripts": {
        "start": "electron .",
        "build": "electron-builder"
    }
}
```
