"""Launch targets are looked up once per component, off the event loop, before any start."""

import asyncio
import threading
import time
from collections import Counter
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.hosts import LocalHostLauncher
from slow_thinker_ii.application import StartupFailed
from slow_thinker_ii.catalog import ComponentRef
from slow_thinker_ii.contracts import json_object
from slow_thinker_ii.graphs import RunPlan
from support.examples import J2, journey_plan
from support.log import RecordingLog

from .plans import fixture_plan
from .process_fixture import RUN, Targets, launched, launcher, settings


class CountingTargets(Targets):
    """Slow like a verified installation; counts lookups; `missing` names an uninstalled type."""

    def __init__(self, program: Path, delay: float = 0, missing: str | None = None) -> None:
        super().__init__(program)
        self.delay, self.missing = delay, missing
        self.calls: Counter[tuple[str, str]] = Counter()
        self.busy = False
        self._lock = threading.Lock()

    def interpreter(self, ref: ComponentRef) -> Path:
        self._count("interpreter", ref)
        self.busy = True
        time.sleep(self.delay)
        self.busy = False
        if ref.type == self.missing:
            raise LookupError(f"No configured resolution installs {ref}")
        return super().interpreter(ref)

    def module(self, ref: ComponentRef) -> str:
        self._count("module", ref)
        return super().module(ref)

    def _count(self, kind: str, ref: ComponentRef) -> None:
        with self._lock:
            self.calls[(kind, str(ref))] += 1


async def test_each_component_is_looked_up_once_per_launch(tmp_path: Path) -> None:
    targets = CountingTargets(launcher(tmp_path))
    plan = fixture_plan("serve", "serve", embedded="serve")
    log = RecordingLog()
    async with launched(plan, settings(tmp_path), targets, log):
        pass
    assert len(log.of("host.ready")) == 3
    assert targets.calls == Counter(
        {("interpreter", "fixture@1.0.0"): 1, ("module", "fixture@1.0.0"): 1}
    )


async def test_a_slow_launch_target_does_not_block_the_event_loop(tmp_path: Path) -> None:
    targets = CountingTargets(launcher(tmp_path), delay=0.4)
    ticks_while_looking_up = 0

    async def tick() -> None:
        nonlocal ticks_while_looking_up
        while True:
            await asyncio.sleep(0.01)
            if targets.busy:
                ticks_while_looking_up += 1

    ticker = asyncio.create_task(tick())
    async with launched(fixture_plan("serve"), settings(tmp_path), targets, RecordingLog()):
        pass
    ticker.cancel()
    assert ticks_while_looking_up >= 10


async def failed_launch(tmp_path: Path, plan: RunPlan, missing: str) -> tuple[str, RecordingLog]:
    log, host_settings = RecordingLog(), settings(tmp_path)
    targets = CountingTargets(launcher(tmp_path), missing=missing)
    with pytest.raises(StartupFailed) as failed:
        await LocalHostLauncher(targets, host_settings).launch(RUN, plan, log)
    assert not host_settings.workspace.exists()
    return str(failed.value), log


def outcomes(log: RecordingLog) -> list[tuple[str | None, str]]:
    return [(event.node_id, str(json_object(event.data["error"])["code"])) for event in log.events]


async def test_every_host_of_an_uninstalled_component_fails_and_none_starts(
    tmp_path: Path,
) -> None:
    detail, log = await failed_launch(tmp_path, fixture_plan("serve", "serve"), "fixture")
    cause = "it is not installed: No configured resolution installs fixture@1.0.0"
    assert detail == f"Fixture in Worker 1 could not start: {cause}"
    assert outcomes(log) == [("w1", "launch_failed"), ("w2", "launch_failed")]


async def test_hosts_of_installed_components_are_not_started_either(tmp_path: Path) -> None:
    detail, log = await failed_launch(tmp_path, journey_plan(J2), "router")
    cause = "it is not installed: No configured resolution installs router@1.0.0"
    assert detail == f"Router in Judge could not start: {cause}"
    assert outcomes(log) == [("judge", "stopped"), ("judge", "launch_failed")]
    assert [event.data["position"] for event in log.events] == ["node", "output"]
