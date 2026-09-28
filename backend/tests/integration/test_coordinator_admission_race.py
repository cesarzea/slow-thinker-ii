"""Shutdown retains ownership of a Start whose durable admission is still in flight."""

import asyncio
from pathlib import Path
from threading import Event

import pytest
from slow_thinker_ii.application import CommandResult, PreparedStart
from support.coordinator import Environment, coordinator_case, eventually


async def test_shutdown_during_admission_cannot_orphan_a_committed_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = coordinator_case(tmp_path, shutdown=0.02)
    entered, release = Event(), Event()
    admit = case.commands.admit

    def delayed(command: str, prepared: PreparedStart) -> CommandResult:
        entered.set()
        assert release.wait(5)
        return admit(command, prepared)

    monkeypatch.setattr(case.commands, "admit", delayed)
    request = asyncio.create_task(case.coordinator.start("start", case.base.prepared().intent))
    await eventually(entered.is_set)
    report = await case.coordinator.close()
    assert report.commands == ("start:start",)
    release.set()
    receipt = (await request).receipt
    assert receipt.target_id is not None
    await eventually(lambda: not case.coordinator.pending().runs)
    assert (
        isinstance(case.preparer.environment, Environment) and case.preparer.environment.opened == 0
    )
    with case.runs.begin() as transaction:
        assert transaction.run(receipt.target_id).reason == "runtime_shutdown"
    assert not (await case.coordinator.close()).commands
