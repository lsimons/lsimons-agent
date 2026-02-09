"""Tests for tools module."""

import tempfile
from pathlib import Path

from lsimons_agent.tools import bash, edit_file, execute, read_file, write_file


def test_read_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        result = read_file(f.name)
        assert result == "hello world"


def test_read_file_not_found():
    try:
        read_file("/nonexistent/file.txt")
        raise AssertionError("Should have raised FileNotFoundError")
    except FileNotFoundError:
        pass


def test_write_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "test.txt"
        result = write_file(str(path), "test content")
        assert result == "OK"
        assert path.read_text() == "test content"


def test_write_file_creates_parent_dirs():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / "subdir" / "nested" / "test.txt"
        result = write_file(str(path), "nested content")
        assert result == "OK"
        assert path.read_text() == "nested content"


def test_edit_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        result = edit_file(f.name, "world", "universe")
        assert result == "OK"
        assert Path(f.name).read_text() == "hello universe"


def test_edit_file_string_not_found():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello world")
        f.flush()
        try:
            edit_file(f.name, "foo", "bar")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "not found" in str(e)


def test_edit_file_string_not_unique():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("hello hello hello")
        f.flush()
        try:
            edit_file(f.name, "hello", "hi")
            raise AssertionError("Should have raised ValueError")
        except ValueError as e:
            assert "3 times" in str(e)


def test_bash_simple_command():
    result = bash("echo hello")
    assert result == "hello"


def test_bash_command_with_error():
    result = bash("ls /nonexistent_directory_12345")
    assert "exit code" in result or "No such file" in result


def test_bash_returns_no_output():
    result = bash("true")
    assert result == "(no output)"


def test_execute_read_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("content")
        f.flush()
        result = execute("read_file", {"path": f.name})
        assert result == "content"


def test_execute_write_file():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "test.txt")
        result = execute("write_file", {"path": path, "content": "data"})
        assert result == "OK"


def test_execute_edit_file():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("old text")
        f.flush()
        result = execute("edit_file", {"path": f.name, "old_string": "old", "new_string": "new"})
        assert result == "OK"


def test_execute_bash():
    result = execute("bash", {"command": "echo test"})
    assert result == "test"


def test_execute_unknown_tool():
    result = execute("unknown_tool", {})
    assert "Unknown tool" in result
