"""Host processes seen from outside: their pid files in the run directory and their reaping."""

import os
from pathlib import Path


def host_pids(run_directory: Path) -> dict[str, int]:
    """`<node>.<position>` → pid, as each fixture host wrote it when it started."""
    return {
        path.name.removesuffix(".pid"): int(path.read_text())
        for path in run_directory.glob("*.pid")
    }


def is_running(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    return True
