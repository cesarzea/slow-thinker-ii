"""An independently owned child exposes a trusted identity without inspecting other processes."""

import asyncio
import os
import subprocess
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from pathlib import Path

import psutil
from slow_thinker_ii.application import ProcessIdentity


@asynccontextmanager
async def owned_child(directory: Path, *, stubborn: bool = False) -> AsyncIterator[ProcessIdentity]:
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
        child = psutil.Process(process.pid)
        yield ProcessIdentity(
            process.pid,
            child.create_time(),
            child.exe(),
            tuple(child.cmdline()),
            marker,
            str(directory),
            os.getpgid(process.pid),
            os.getsid(process.pid),
        )
    finally:
        if process.poll() is None:
            process.kill()
        process.wait(timeout=5)
