"""An independently owned child exposes a trusted identity without inspecting other processes."""

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import psutil
from slow_thinker_ii.application import ProcessIdentity


def _process_identity(pid: int, marker: str, directory: Path) -> ProcessIdentity:
    child = psutil.Process(pid)
    return ProcessIdentity(
        pid,
        child.create_time(),
        child.exe(),
        tuple(child.cmdline()),
        marker,
        str(directory),
        os.getpgid(pid),
        os.getsid(pid),
    )


@asynccontextmanager
async def owned_child(
    directory: Path, *, stubborn: bool = False
) -> AsyncGenerator[ProcessIdentity]:
    marker = "test-owned-process"
    script = "import time,pathlib; pathlib.Path('ready').touch(); time.sleep(30)"
    if stubborn:
        script = "import signal; signal.signal(signal.SIGTERM, signal.SIG_IGN); " + script
    process = subprocess.Popen(
        [sys.executable, "-I", "-c", script],
        cwd=directory,
        env={"SLOW_THINKER_PROCESS_OWNER": marker},
        start_new_session=True,
    )
    try:
        async with asyncio.timeout(5):
            while not (directory / "ready").exists():
                await asyncio.sleep(0.005)
        yield _process_identity(process.pid, marker, directory)
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
