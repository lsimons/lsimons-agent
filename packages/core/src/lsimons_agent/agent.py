"""Agent loop for interactive conversation."""

import json

from lsimons_agent.llm import chat
from lsimons_agent.tools import TOOLS, bash, execute

SYSTEM_PROMPT = """\
You are a coding assistant. You help the user by reading, writing, and editing \
files, and running shell commands.

When editing files, use edit_file with the exact string to replace - include \
enough context to make the match unique.

Be concise. Execute tasks directly without asking for confirmation."""


def process_message(messages: list[dict], user_message: str):
    """
    Process a user message and yield events.

    Yields tuples of (event_type, data):
    - ("text", content) - Agent text response
    - ("tool", {"name": name, "args": args}) - Tool being executed
    - ("done", None) - Processing complete

    Modifies messages list in place.
    """
    messages.append({"role": "user", "content": user_message})

    while True:
        response = chat(messages, tools=TOOLS)
        message = response["choices"][0]["message"]
        content = message.get("content", "")
        tool_calls = message.get("tool_calls", [])

        if content:
            yield ("text", content)

        if not tool_calls:
            messages.append(message)
            break

        messages.append(message)
        for tool_call in tool_calls:
            fn = tool_call["function"]
            name = fn["name"]
            args = json.loads(fn["arguments"])

            yield ("tool", {"name": name, "args": args})

            try:
                result = execute(name, args)
            except Exception as e:
                result = f"Error: {e}"

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "content": result,
            })

    yield ("done", None)


def new_conversation() -> list[dict]:
    """Create a new conversation with system prompt."""
    return [{"role": "system", "content": SYSTEM_PROMPT}]


def run():
    """Run the interactive CLI agent loop."""
    messages = new_conversation()

    print("lsimons-agent")
    print("-" * 40)
    print("Type a message, /clear to reset, !cmd for bash, Ctrl+C to exit")
    print()

    while True:
        try:
            user_input = input("You: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not user_input:
            continue

        if user_input == "/clear":
            messages = new_conversation()
            print("Cleared.")
            continue

        if user_input.startswith("!"):
            print(bash(user_input[1:]))
            continue

        for event_type, data in process_message(messages, user_input):
            if event_type == "text":
                print(f"\nAgent: {data}")
            elif event_type == "tool":
                print(f"[Tool: {data['name']}({_format_args(data['args'])})]")
            elif event_type == "done":
                print()


def _format_args(args: dict) -> str:
    """Format tool arguments for display."""
    parts = []
    for k, v in args.items():
        if isinstance(v, str) and len(v) > 30:
            v = v[:30] + "..."
        parts.append(f"{k}={v!r}")
    return ", ".join(parts)
