"""LLM client for OpenAI-compatible APIs."""

import os

import httpx


def chat(messages: list[dict], tools: list[dict] | None = None, model: str | None = None) -> dict:
    """Send messages to LLM and return raw API response dict."""
    base_url = os.environ.get("LLM_BASE_URL", "http://localhost:8000")
    auth_token = os.environ.get("LLM_AUTH_TOKEN", "")
    model = model or os.environ.get("LLM_DEFAULT_MODEL", "mock-model")

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 4096,
    }
    if tools:
        payload["tools"] = tools

    headers = {}
    if auth_token:
        headers["Authorization"] = f"Bearer {auth_token}"

    response = httpx.post(
        f"{base_url}/chat/completions",
        json=payload,
        headers=headers,
        timeout=120.0,
    )
    response.raise_for_status()
    return response.json()
