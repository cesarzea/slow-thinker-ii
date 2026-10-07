"""Shutdown: close stdin, wait, terminate, kill — within the budget, and never raising."""

import time
from pathlib import Path

from slow_thinker_ii.adapters.hosts import LocalHostLauncher
from slow_thinker_ii.engine import CallFailure
from support.log import RecordingLog

from .owned_process import host_pids, is_running
from .plans import fixture_plan
from .process_fixture import RUN, Targets, context, launcher, settings


async def close_timed(
    tmp_path: Path, mode: str, shutdown_seconds: float = 1.5
) -> tuple[float, list[int]]:
    """Launches one host in `mode`, closes the run twice; returns the first close's duration."""
    host_settings = settings(tmp_path, shutdown_seconds=shutdown_seconds)
    launch = LocalHostLauncher(Targets(launcher(tmp_path)), host_settings)
    hosts = await launch.launch(RUN, fixture_plan(mode), RecordingLog())
    pids = list(host_pids(host_settings.workspace / RUN).values())
    started = time.monotonic()
    await hosts.close()
    elapsed = time.monotonic() - started
    await hosts.close()
    assert not (host_settings.workspace / RUN).exists()
    assert await hosts.activate(context(), "late") == CallFailure(
        "host_failed", "The component host is not running."
    )
    return elapsed, pids


async def test_a_host_stops_when_its_standard_input_closes(tmp_path: Path) -> None:
    elapsed, pids = await close_timed(tmp_path, "serve", shutdown_seconds=3)
    assert elapsed < 0.9 and not any(is_running(pid) for pid in pids)


async def test_a_host_ignoring_stdin_and_termination_is_killed_within_the_budget(
    tmp_path: Path,
) -> None:
    elapsed, pids = await close_timed(tmp_path, "stubborn")
    assert 0.9 < elapsed < 2.5 and not any(is_running(pid) for pid in pids)


async def test_a_host_ignoring_stdin_is_terminated(tmp_path: Path) -> None:
    elapsed, pids = await close_timed(tmp_path, "linger")
    assert 0.4 < elapsed < 1.4 and not any(is_running(pid) for pid in pids)
