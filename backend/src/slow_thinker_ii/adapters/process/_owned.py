"""Retain the exact child handle and reap it with bounded graceful/forced cleanup."""

import asyncio
from contextlib import suppress
from dataclasses import dataclass

from ._launch import ProcessLaunch
from ._secrets import secret_environment


@dataclass(frozen=True)
class ProcessOutcome:
    pid: int
    returncode: int | None
    forced: bool


async def wait_exit(process: asyncio.subprocess.Process, seconds: float) -> bool:
    try:
        async with asyncio.timeout(seconds):
            await process.wait()
    except TimeoutError:
        return False
    return True


class OwnedProcess:
    def __init__(self, launch: ProcessLaunch) -> None:
        self._launch = launch
        self._process: asyncio.subprocess.Process | None = None
        self._forced = False

    async def start(self) -> asyncio.subprocess.Process:
        if self._process is not None:
            raise RuntimeError("A process handle cannot be reused")
        self._process = await asyncio.create_subprocess_exec(
            str(self._launch.python),
            "-B",
            "-I",
            "-m",
            self._launch.module,
            str(self._launch.bootstrap),
            cwd=self._launch.workspace,
            env={
                "PATH": str(self._launch.python.parent),
                **secret_environment(self._launch.secrets),
            },
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            limit=self._launch.max_message_bytes,
            start_new_session=True,
        )
        return self._process

    def outcome(self) -> ProcessOutcome | None:
        process = self._process
        return (
            None
            if process is None
            else ProcessOutcome(process.pid, process.returncode, self._forced)
        )

    async def stop(self) -> None:
        process = self._process
        if process is None or process.returncode is not None:
            return
        if process.stdin is not None:
            process.stdin.close()
        interval = self._launch.shutdown_seconds / 3
        if await wait_exit(process, interval):
            return
        self._forced = True
        with suppress(ProcessLookupError):
            process.terminate()
        if await wait_exit(process, interval):
            return
        with suppress(ProcessLookupError):
            process.kill()
        if not await wait_exit(process, interval):
            raise RuntimeError("Owned component process did not exit within its cleanup limit")
