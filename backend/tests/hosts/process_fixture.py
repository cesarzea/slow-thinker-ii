"""Launch targets, settings and contexts for real host processes in adapter tests."""

import sys
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from slow_thinker_ii.adapters.hosts import HostSettings, LocalHostLauncher
from slow_thinker_ii.application import RunHosts
from slow_thinker_ii.catalog import ComponentRef
from slow_thinker_ii.engine import CallContext, Position
from slow_thinker_ii.graphs import RunPlan
from support.log import RecordingLog

FIXTURE = Path(__file__).with_name("component_fixture.py")
PROTOCOL_FIXTURE = Path(__file__).with_name("protocol_fixture.py")
RUN = "run-1"


class Targets:
    """Fixture hosts run through a launcher script; LLM Call, Router and Memory are the real
    packages."""

    def __init__(self, launcher: Path) -> None:
        self.launcher = launcher

    def interpreter(self, ref: ComponentRef) -> Path:
        if ref.type == "fixture":
            return self.launcher
        if ref.type in ("llm-call", "router", "memory"):
            return Path(sys.executable)
        raise LookupError(f"{ref} is not installed")

    def module(self, ref: ComponentRef) -> str:
        return "fixture" if ref.type == "fixture" else "slow_thinker_" + ref.type.replace("-", "_")


def launcher(directory: Path, program: Path = FIXTURE) -> Path:
    """An executable that receives the adapter's argument vector and runs `program`."""
    path = directory / "fixture-python"
    python = sys.executable
    path.write_text(
        f"#!{python}\nimport json, os, sys\n"
        f"os.execv({python!r}, [{python!r}, '-B', {str(program)!r}, sys.argv[-1], "
        "json.dumps(sys.argv[1:])])\n"
    )
    path.chmod(0o700)
    return path


def settings(
    directory: Path,
    *,
    llm_base_url: str = "http://127.0.0.1:9/v1",
    startup_seconds: float = 20,
    shutdown_seconds: float = 1.5,
    max_message_bytes: int = 65_536,
) -> HostSettings:
    return HostSettings(
        workspace=directory / "workspace",
        llm_base_url=llm_base_url,
        mcp_url="http://127.0.0.1:9/mcp",
        startup_seconds=startup_seconds,
        shutdown_seconds=shutdown_seconds,
        max_message_bytes=max_message_bytes,
    )


def context(node: str = "w1", position: Position = "node", budget_ms: int = 5000) -> CallContext:
    return CallContext(RUN, node, position, "a1", f"grant-{node}-{position}", budget_ms)


@asynccontextmanager
async def launched(
    plan: RunPlan, host_settings: HostSettings, targets: Targets, log: RecordingLog
) -> AsyncGenerator[RunHosts]:
    """The run's hosts, always closed afterwards."""
    hosts = await LocalHostLauncher(targets, host_settings).launch(RUN, plan, log)
    try:
        yield hosts
    finally:
        await hosts.close()
