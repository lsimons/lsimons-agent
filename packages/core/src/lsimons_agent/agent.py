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


def run():
    """Run the interactive agent loop."""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

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
            messages = [messages[0]]  # Keep system prompt
            print("Cleared.")
            continue

        if user_input.startswith("!"):
            # Direct bash execution
            print(bash(user_input[1:]))
            continue

        messages.append({"role": "user", "content": user_input})

        # Agent loop: call LLM, execute tools, repeat until done
        while True:
            response = chat(messages, tools=TOOLS)
            message = response["choices"][0]["message"]
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            if content:
                print()
                print(f"Agent: {content}")

            if not tool_calls:
                messages.append(message)
                print()
                break

            # Execute tools
            messages.append(message)
            for tool_call in tool_calls:
                fn = tool_call["function"]
                name = fn["name"]
                args = json.loads(fn["arguments"])

                print(f"[Tool: {name}({_format_args(args)})]")

                try:
                    result = execute(name, args)
                except Exception as e:
                    result = f"Error: {e}"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": result,
                })


def _format_args(args: dict) -> str:
    """Format tool arguments for display."""
    parts = []
    for k, v in args.items():
        if isinstance(v, str) and len(v) > 30:
            v = v[:30] + "..."
        parts.append(f"{k}={v!r}")
    return ", ".join(parts)
