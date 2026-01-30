"""Tests for web server module."""

import json

from lsimons_agent_web.server import TEMPLATES_DIR, app, event_stream


def test_templates_dir_exists():
    assert TEMPLATES_DIR.exists()
    assert TEMPLATES_DIR.is_dir()


def test_templates_has_index():
    assert (TEMPLATES_DIR / "index.html").exists()


def test_app_has_routes():
    routes = [route.path for route in app.routes]
    assert "/" in routes
    assert "/chat" in routes
    assert "/clear" in routes


def test_event_stream_formats_text_event():
    # Create a mock generator that yields a text event
    def mock_process_message(messages, user_message):
        yield ("text", "Hello world")
        yield ("done", None)

    # Temporarily replace process_message
    import lsimons_agent_web.server as server_module

    original = server_module.process_message
    server_module.process_message = mock_process_message

    try:
        events = list(event_stream("test"))
        assert len(events) == 2

        # Check text event
        assert events[0].startswith("event: text\n")
        assert "Hello world" in events[0]
        data_line = events[0].split("\n")[1]
        assert data_line.startswith("data: ")
        parsed = json.loads(data_line[6:])
        assert parsed["content"] == "Hello world"

        # Check done event
        assert events[1] == "event: done\ndata: {}\n\n"
    finally:
        server_module.process_message = original


def test_event_stream_formats_tool_event():
    def mock_process_message(messages, user_message):
        yield ("tool", {"name": "read_file", "args": {"path": "foo.txt"}})
        yield ("done", None)

    import lsimons_agent_web.server as server_module

    original = server_module.process_message
    server_module.process_message = mock_process_message

    try:
        events = list(event_stream("test"))
        assert len(events) == 2

        # Check tool event
        assert events[0].startswith("event: tool\n")
        data_line = events[0].split("\n")[1]
        parsed = json.loads(data_line[6:])
        assert parsed["name"] == "read_file"
        assert parsed["args"]["path"] == "foo.txt"
    finally:
        server_module.process_message = original
