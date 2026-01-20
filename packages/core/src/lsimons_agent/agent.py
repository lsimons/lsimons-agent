"""Agent loop for interactive conversation."""

from lsimons_agent.llm import chat

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
    print("Type a message, /clear to reset, Ctrl+C to exit")
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

        messages.append({"role": "user", "content": user_input})

        # Get response from LLM
        response = chat(messages)
        message = response["choices"][0]["message"]
        content = message.get("content", "")

        messages.append(message)

        print()
        print(f"Agent: {content}")
        print()
