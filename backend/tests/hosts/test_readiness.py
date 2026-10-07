"""Readiness failures stop every host, record `host.failed` and raise `StartupFailed`."""

import time
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.hosts import LocalHostLauncher
from slow_thinker_ii.application import StartupFailed
from slow_thinker_ii.catalog import ComponentRef
from slow_thinker_ii.graphs import RunPlan
from support.log import RecordingLog

from .owned_process import host_pids, is_running
from .plans import fixture_plan
from .process_fixture import PROTOCOL_FIXTURE, RUN, Targets, launcher, settings


async def failed_start(
    tmp_path: Path,
    plan: RunPlan,
    targets: Targets | None = None,
    log: RecordingLog | None = None,
    startup_seconds: float = 20,
) -> tuple[str, RecordingLog]:
    log = log or RecordingLog()
    host_settings = settings(tmp_path, startup_seconds=startup_seconds)
    launch = LocalHostLauncher(targets or Targets(launcher(tmp_path)), host_settings)
    with pytest.raises(StartupFailed) as failed:
        await launch.launch(RUN, plan, log)
    assert not (host_settings.workspace / RUN).exists()
    return str(failed.value), log


@pytest.mark.parametrize(
    ("mode", "code", "cause"),
    [
        ("exit", "exited", "Fixture startup failed: told to exit."),
        ("malformed", "protocol_error", "it wrote output that is not the protocol's JSON-RPC."),
    ],
)
async def test_a_host_that_is_not_ready_fails_the_start(
    tmp_path: Path, mode: str, code: str, cause: str
) -> None:
    detail, log = await failed_start(tmp_path, fixture_plan(mode))
    assert detail == f"Fixture in Worker 1 could not start: {cause}"
    (failed,) = log.of("host.failed")
    assert failed.node_id == "w1"
    assert failed.data == {
        "position": "node",
        "component": "fixture@1.0.0",
        "error": {"code": code, "message": detail},
    }
    assert not log.of("host.ready")


@pytest.mark.parametrize(
    ("mode", "code", "cause"),
    [
        ("wrong_tools", "tools_mismatch", "it exposes other instead of only the activate tool."),
        (
            "bad_schemas",
            "tools_mismatch",
            "its activate tool does not have the protocol's schemas.",
        ),
        ("old_protocol", "protocol_error", "it does not support the MCP protocol 2026-07-28."),
        ("extra_capability", "protocol_error", "it offers prompts, tools instead of tools only."),
        ("discover_error", "protocol_error", "it failed the protocol handshake: Method not found."),
        ("huge_hello", "protocol_error", "it sent a message above the size limit."),
    ],
)
async def test_a_host_breaking_the_protocol_fails_the_start(
    tmp_path: Path, mode: str, code: str, cause: str
) -> None:
    targets = Targets(launcher(tmp_path, PROTOCOL_FIXTURE))
    detail, log = await failed_start(tmp_path, fixture_plan(mode), targets)
    assert detail == f"Fixture in Worker 1 could not start: {cause}"
    assert log.of("host.failed")[0].data["error"] == {"code": code, "message": detail}


async def test_a_silent_host_fails_after_the_startup_timeout(tmp_path: Path) -> None:
    started = time.monotonic()
    detail, log = await failed_start(tmp_path, fixture_plan("hang"), startup_seconds=1)
    assert detail == "Fixture in Worker 1 could not start: it was not ready within 1 seconds."
    assert log.of("host.failed")[0].data["error"] == {"code": "not_ready", "message": detail}
    assert time.monotonic() - started < 5


async def test_one_failure_stops_hosts_that_are_still_starting(tmp_path: Path) -> None:
    run_directory = tmp_path / "workspace" / RUN
    seen: dict[str, int] = {}

    def remember() -> None:
        seen.update(host_pids(run_directory))

    log = RecordingLog()
    log.when("host.ready", remember)
    detail, _ = await failed_start(tmp_path, fixture_plan("serve", "hang", "exit"), log=log)
    assert detail == "Fixture in Worker 3 could not start: Fixture startup failed: told to exit."
    outcomes = {event.node_id: event.kind for event in log.events}
    assert outcomes == {"w1": "host.ready", "w2": "host.failed", "w3": "host.failed"}
    (stopped,) = [event for event in log.of("host.failed") if event.node_id == "w2"]
    assert stopped.data["error"] == {
        "code": "stopped",
        "message": "Fixture in Worker 2 was stopped before it was ready.",
    }
    assert seen and not any(is_running(pid) for pid in seen.values())


class MissingInterpreter(Targets):
    def interpreter(self, ref: ComponentRef) -> Path:
        return Path("/nonexistent/python")


async def test_launch_target_failures_are_startup_failures(tmp_path: Path) -> None:
    detail, log = await failed_start(tmp_path, fixture_plan("serve"), MissingInterpreter(tmp_path))
    assert detail.startswith(
        "Fixture in Worker 1 could not start: its interpreter could not be started:"
    )
    assert log.of("host.failed")[0].data["error"] == {"code": "launch_failed", "message": detail}


async def test_an_uninstalled_component_fails_the_start(tmp_path: Path) -> None:
    class Nothing(Targets):
        def interpreter(self, ref: ComponentRef) -> Path:
            raise LookupError(f"{ref} has no installation")

    detail, _ = await failed_start(tmp_path, fixture_plan("serve"), Nothing(tmp_path))
    cause = "it is not installed: fixture@1.0.0 has no installation"
    assert detail == f"Fixture in Worker 1 could not start: {cause}"
