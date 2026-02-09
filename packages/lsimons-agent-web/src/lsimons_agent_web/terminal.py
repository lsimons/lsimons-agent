"""PTY terminal management for browser-based terminal."""

import contextlib
import fcntl
import glob
import os
import pty
import select
import struct
import termios
import threading
from queue import Empty, Queue


class Terminal:
    """Manages a PTY-based terminal session."""

    SCROLLBACK_SIZE = 64 * 1024  # 64KB scrollback buffer

    def __init__(
        self,
        shell: str = "/bin/zsh",
        command: list[str] | None = None,
        cwd: str | None = None,
    ):
        self.shell = shell
        self.command = command  # Command to run instead of interactive shell
        self.cwd = cwd  # Working directory for the terminal
        self.master_fd: int | None = None
        self.pid: int | None = None
        self.output_queue: Queue[bytes] = Queue()
        self._reader_thread: threading.Thread | None = None
        self._running = False
        self._scrollback: bytearray = bytearray()
        self._scrollback_lock = threading.Lock()

    def start(self) -> None:
        """Fork a PTY and spawn the shell or command."""
        if self._running:
            return

        pid, fd = pty.fork()
        if pid == 0:
            # Child process - change to working directory
            if self.cwd:
                with contextlib.suppress(OSError):
                    os.chdir(self.cwd)

            # Set up environment for colors and proper shell detection
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["CLICOLOR"] = "1"
            env["CLICOLOR_FORCE"] = "1"
            env["COLORTERM"] = "truecolor"
            env["TERM_PROGRAM"] = "lsimons-agent"
            env["LC_TERMINAL"] = "lsimons-agent"
            # Remove ZDOTDIR so zsh uses $HOME for .zshrc
            env.pop("ZDOTDIR", None)

            # Ensure PATH includes common bin directories (app bundles have minimal PATH)
            home = os.path.expanduser("~")
            extra_paths = [
                f"{home}/git/lsimons/lsimons-agent/.venv/bin",
                f"{home}/.local/bin",
                f"{home}/.cargo/bin",
                "/opt/homebrew/bin",
                "/opt/homebrew/sbin",
                "/usr/local/bin",
                "/usr/local/sbin",
            ]
            # Add NVM node bin directories (glob for any installed version)
            nvm_paths = glob.glob(f"{home}/.local/share/nvm/versions/node/*/bin")
            nvm_paths += glob.glob(f"{home}/.nvm/versions/node/*/bin")
            extra_paths.extend(sorted(nvm_paths, reverse=True))  # Prefer newer versions
            current_path = env.get("PATH", "/usr/bin:/bin")
            env["PATH"] = ":".join(extra_paths) + ":" + current_path

            # Exec shell or command
            if self.command:
                os.execvpe(self.command[0], self.command, env)
            else:
                # Login shell - should source .zshrc for interactive login
                os.execvpe(self.shell, [self.shell, "-l"], env)
        else:
            # Parent process
            self.pid = pid
            self.master_fd = fd
            self._running = True

            # Start reader thread
            self._reader_thread = threading.Thread(target=self._read_loop, daemon=True)
            self._reader_thread.start()

    def _read_loop(self) -> None:
        """Read from PTY and queue output (runs in thread)."""
        while self._running and self.master_fd is not None:
            try:
                ready, _, _ = select.select([self.master_fd], [], [], 0.1)
                if ready:
                    data = os.read(self.master_fd, 4096)
                    if data:
                        self.output_queue.put(data)
                        # Store in scrollback buffer
                        with self._scrollback_lock:
                            self._scrollback.extend(data)
                            # Trim if too large
                            if len(self._scrollback) > self.SCROLLBACK_SIZE:
                                excess = len(self._scrollback) - self.SCROLLBACK_SIZE
                                del self._scrollback[:excess]
                    else:
                        # EOF - process exited
                        self._running = False
                        break
            except OSError:
                # FD closed
                self._running = False
                break

    def write(self, data: bytes) -> None:
        """Send input to the PTY."""
        if self.master_fd is not None:
            os.write(self.master_fd, data)

    def read_nowait(self) -> bytes | None:
        """Non-blocking read from output queue."""
        try:
            return self.output_queue.get_nowait()
        except Empty:
            return None

    def resize(self, rows: int, cols: int) -> None:
        """Resize the terminal window."""
        if self.master_fd is not None:
            winsize = struct.pack("HHHH", rows, cols, 0, 0)
            fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ, winsize)

    def refresh(self) -> None:
        """Trigger terminal redraw by sending Ctrl+L."""
        if self.master_fd is not None:
            os.write(self.master_fd, b"\x0c")  # Ctrl+L

    def get_scrollback(self) -> bytes:
        """Get the scrollback buffer contents."""
        with self._scrollback_lock:
            return bytes(self._scrollback)

    def stop(self) -> None:
        """Stop the terminal session."""
        self._running = False

        if self.master_fd is not None:
            with contextlib.suppress(OSError):
                os.close(self.master_fd)
            self.master_fd = None

        if self.pid is not None:
            try:
                os.kill(self.pid, 9)
                os.waitpid(self.pid, 0)
            except (OSError, ChildProcessError):
                pass
            self.pid = None

        if self._reader_thread is not None:
            self._reader_thread.join(timeout=1.0)
            self._reader_thread = None

    def is_running(self) -> bool:
        """Check if terminal is running."""
        return self._running
