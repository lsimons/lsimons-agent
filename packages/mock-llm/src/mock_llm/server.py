"""Mock LLM server that returns canned responses."""

import json
import uuid
from pathlib import Path

from fastapi import FastAPI

app = FastAPI()

# Load scenarios from file
SCENARIOS_PATH = Path(__file__).parent.parent.parent / "scenarios.json"
with open(SCENARIOS_PATH) as f:
    SCENARIOS = json.load(f)


def find_scenario(user_message: str) -> dict | None:
    """Find a scenario matching the user message."""
    user_lower = user_message.lower()
    for scenario in SCENARIOS["scenarios"]:
        if scenario["trigger"] in user_lower:
            return scenario
    return None


def get_step_index(messages: list[dict]) -> int:
    """Count tool result messages to determine current step."""
    return sum(1 for m in messages if m.get("role") == "tool")


def build_response(content: str | None, tool_calls: list | None = None) -> dict:
    """Build OpenAI-format response."""
    message = {"role": "assistant", "content": content}
    if tool_calls:
        message["tool_calls"] = tool_calls

    return {
        "id": f"mock-{uuid.uuid4().hex[:8]}",
        "object": "chat.completion",
        "model": "mock-model",
        "choices": [
            {
                "index": 0,
                "message": message,
                "finish_reason": "tool_calls" if tool_calls else "stop",
            }
        ],
    }


@app.post("/chat/completions")
def chat_completions(request: dict):
    """Handle chat completion requests."""
    messages = request.get("messages", [])

    # Get last user message
    last_user_message = ""
    for msg in reversed(messages):
        if msg.get("role") == "user" and msg.get("content"):
            last_user_message = msg["content"]
            break

    # Find matching scenario
    scenario = find_scenario(last_user_message)
    if not scenario:
        return build_response(SCENARIOS["default_response"]["content"])

    # Determine step based on tool result count
    step_index = get_step_index(messages)
    if step_index >= len(scenario["steps"]):
        return build_response("Scenario complete.")

    step = scenario["steps"][step_index]
    return build_response(
        step["response"].get("content"),
        step["response"].get("tool_calls"),
    )


@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}


def main():
    """Run the mock server."""
    import uvicorn

    print("Starting mock LLM server on http://localhost:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
