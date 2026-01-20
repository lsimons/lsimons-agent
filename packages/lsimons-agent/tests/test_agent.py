"""Tests for agent module."""

from lsimons_agent.agent import SYSTEM_PROMPT, _format_args, new_conversation


def test_new_conversation():
    messages = new_conversation()
    assert len(messages) == 1
    assert messages[0]["role"] == "system"
    assert messages[0]["content"] == SYSTEM_PROMPT


def test_new_conversation_returns_new_list():
    messages1 = new_conversation()
    messages2 = new_conversation()
    assert messages1 is not messages2


def test_format_args_simple():
    result = _format_args({"path": "foo.txt"})
    assert result == "path='foo.txt'"


def test_format_args_multiple():
    result = _format_args({"path": "foo.txt", "content": "hello"})
    assert "path='foo.txt'" in result
    assert "content='hello'" in result


def test_format_args_truncates_long_strings():
    long_string = "a" * 100
    result = _format_args({"content": long_string})
    assert "..." in result
    assert len(result) < 100


def test_format_args_empty():
    result = _format_args({})
    assert result == ""


def test_system_prompt_content():
    assert "coding assistant" in SYSTEM_PROMPT
    assert "edit_file" in SYSTEM_PROMPT
