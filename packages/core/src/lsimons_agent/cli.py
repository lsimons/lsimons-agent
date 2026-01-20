"""CLI entry point for lsimons-agent."""

from lsimons_agent.llm import chat


def main():
    """Main entry point."""
    print("lsimons-agent")
    print("-" * 40)

    # Send a test message
    messages = [
        {"role": "user", "content": "how are you"}
    ]

    print("You: how are you")
    print()

    response = chat(messages)
    assistant_message = response["choices"][0]["message"]
    content = assistant_message.get("content", "")

    print(f"Agent: {content}")


if __name__ == "__main__":
    main()
