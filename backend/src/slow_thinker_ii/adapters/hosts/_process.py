"""One host process: isolated, in its own session, stopped in three bounded steps."""

import asyncio
from contextlib import suppress
from dataclasses import dataclass, field
from pathlib import Path

TAIL_BYTES = 4096


@dataclass(frozen=True)
class Launch:
    """`<interpreter> -B -I -m <module> <bootstrap>` in `directory`, with only `PATH` set."""

    interpreter: Path
    module: str
    bootstrap: Path
    directory: Path
    max_message_bytes: int
    shutdown_seconds: float


@dataclass
class Diagnostics:
    """The end of the host's standard error and why its connection ended, if it did."""

    tail: bytearray = field(default_factory=bytearray)
    problem: str | None = None

    def add(self, chunk: bytes) -> None:
        self.tail += chunk
        del self.tail[:-TAIL_BYTES]

    def last_line(self) -> str:
        text = self.tail.decode("utf-8", errors="replace")
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        return lines[-1] if lines else ""


class HostProcess:
    """The exact child it started; never reused, and stopped by `stop` without raising."""

    def __init__(self, launch: Launch) -> None:
        self.launch = launch
        self.diagnostics = Diagnostics()
        self._process: asyncio.subprocess.Process | None = None
        self._stopped = False

    @property
    def returncode(self) -> int | None:
        return None if self._process is None else self._process.returncode

    async def start(self) -> asyncio.subprocess.Process:
        launch = self.launch
        self._process = await asyncio.create_subprocess_exec(
            str(launch.interpreter),
            "-B",
            "-I",
            "-m",
            launch.module,
            str(launch.bootstrap),
            cwd=launch.directory,
            env={"PATH": str(launch.interpreter.parent)},
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=launch.max_message_bytes,
            start_new_session=True,
        )
        return self._process

    async def stop(self) -> None:
        """Close stdin, then terminate, then kill, each step waiting a third of the budget."""
        process = self._process
        if process is None or self._stopped:
            return
        self._stopped = True
        interval = self.launch.shutdown_seconds / 3
        assert process.stdin is not None, "hosts are started with pipes"
        process.stdin.close()
        if await _exited(process, interval):
            return
        with suppress(ProcessLookupError):
            process.terminate()
        if await _exited(process, interval):
            return
        with suppress(ProcessLookupError):
            process.kill()
        await _exited(process, interval)


async def _exited(process: asyncio.subprocess.Process, seconds: float) -> bool:
    try:
        async with asyncio.timeout(seconds):
            await process.wait()
    except TimeoutError:
        return False
    return True
