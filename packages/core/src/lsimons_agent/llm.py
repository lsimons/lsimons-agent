"""LLM client for OpenAI-compatible APIs."""

import os

import httpx


def chat(messages: list[dict], tools: list[dict] | None = None, model: str | None = None) -> dict:
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
    base_url = os.environ.get("LLM_BASE_URL", "http://localhost:8000")
    auth_token = os.environ.get("LLM_AUTH_TOKEN", "")
    model = model or os.environ.get("LLM_DEFAULT_MODEL", "mock-model")

    url = f"{base_url}/chat/completions"

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
    }
    if tools:
        payload["tools"] = tools

    headers = {"Content-Type": "application/json"}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = httpx.post(url, json=payload, headers=headers, timeout=120.0)
    response.raise_for_status()
    return response.json()
