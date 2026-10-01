"""Match a persisted owned PID against its creation time and trusted launch fingerprint."""

import os
from pathlib import Path

import psutil

from slow_thinker_ii.application import ProcessIdentity

from ._launch import ProcessLaunch

OWNER_VARIABLE = "SLOW_THINKER_PROCESS_OWNER"


def identify(pid: int, launch: ProcessLaunch) -> ProcessIdentity:
    process = psutil.Process(pid)
    identity = ProcessIdentity(
        pid,
        process.create_time(),
        process.exe(),
        tuple(process.cmdline()),
        launch.ownership.marker if launch.ownership is not None else "",
        str(launch.workspace),
        os.getpgid(pid),
        os.getsid(pid),
    )
    expected = (str(launch.python), "-B", "-I", "-m", launch.module, str(launch.bootstrap))
    if (
        Path(identity.executable).resolve() != launch.python.resolve()
        or identity.command != expected
        or identity.group != pid
        or identity.session != pid
    ):
        raise ValueError("Owned child identity differs from the trusted launch")
    if launch.ownership is not None and process.environ().get(OWNER_VARIABLE) != identity.marker:
        raise ValueError("Owned child marker is unavailable")
    return identity


def verified_process(identity: ProcessIdentity) -> psutil.Process:
    process = psutil.Process(identity.pid)
    if (
        process.create_time() != identity.created_at
        or process.exe() != identity.executable
        or tuple(process.cmdline()) != identity.command
        or process.cwd() != identity.workspace
        or os.getpgid(identity.pid) != identity.group
        or os.getsid(identity.pid) != identity.session
        or process.environ().get(OWNER_VARIABLE) != identity.marker
    ):
        raise ValueError("Owned process identity cannot be verified")
    return process
