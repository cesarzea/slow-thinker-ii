"""Host settings refuse values a launch cannot honour, and launches fail as startups."""

import asyncio
from collections.abc import Callable
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.hosts import HostSettings, LocalHostLauncher
from slow_thinker_ii.application import StartupFailed
from slow_thinker_ii.contracts import json_object
from support.log import RecordingLog

from .owned_process import host_pids, is_running
from .plans import fixture_plan
from .process_fixture import RUN, Targets, launcher, settings


def make(
    workspace: Path = Path("/tmp/hosts"),
    llm_base_url: str = "http://h/v1",
    mcp_url: str = "http://h/mcp",
    startup: float = 20,
    shutdown: float = 5,
    message_bytes: int = 1_048_576,
    concurrency: int = 4,
) -> HostSettings:
    return HostSettings(
        workspace, llm_base_url, mcp_url, startup, shutdown, message_bytes, concurrency
    )


@pytest.mark.parametrize(
    "build",
    [
        lambda: make(workspace=Path("relative")),
        lambda: make(llm_base_url="ftp://h/v1"),
        lambda: make(mcp_url="/mcp"),
        lambda: make(startup=0),
        lambda: make(shutdown=float("inf")),
        lambda: make(startup=True),
        lambda: make(message_bytes=1024),
        lambda: make(concurrency=0),
    ],
)
def test_unusable_settings_are_refused(build: Callable[[], HostSettings]) -> None:
    with pytest.raises(ValueError):
        build()


async def test_an_unwritable_workspace_fails_the_start(tmp_path: Path) -> None:
    (tmp_path / "workspace").write_text("not a directory")
    launch = LocalHostLauncher(Targets(launcher(tmp_path)), settings(tmp_path))
    log = RecordingLog()
    with pytest.raises(StartupFailed, match="its bootstrap document could not be written"):
        await launch.launch(RUN, fixture_plan("serve"), log)
    assert json_object(log.of("host.failed")[0].data["error"])["code"] == "launch_failed"


async def test_cancelling_a_launch_stops_its_hosts(tmp_path: Path) -> None:
    host_settings = settings(tmp_path)
    log = RecordingLog()
    launch = LocalHostLauncher(Targets(launcher(tmp_path)), host_settings)
    starting = asyncio.create_task(launch.launch(RUN, fixture_plan("serve", "hang"), log))
    run_directory = host_settings.workspace / RUN
    async with asyncio.timeout(10):
        while not log.of("host.ready"):
            await asyncio.sleep(0.01)
    pids = host_pids(run_directory)
    starting.cancel()
    with pytest.raises(asyncio.CancelledError):
        await asyncio.gather(starting)
    assert [event.node_id for event in log.of("host.failed")] == ["w2"]
    assert not any(is_running(pid) for pid in pids.values()) and not run_directory.exists()
