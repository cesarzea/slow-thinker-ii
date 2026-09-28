"""Shutdown cancels preparation and runtime work while retaining unresolved task ownership."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.application import CoordinatorUnavailable
from support.coordinator import coordinator_case, eventually


async def test_shutdown_cancels_preflight_without_admission(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.release.clear()
    pending = asyncio.create_task(case.coordinator.start("start", case.base.prepared().intent))
    await case.preparer.entered.wait()
    closed = await case.coordinator.close()
    assert closed.commands == closed.preparations == closed.runs == ()
    assert (await pending).receipt.reason == "preparation_cancelled"
    assert not case.preparer.operation.calls
    with pytest.raises(CoordinatorUnavailable):
        await case.coordinator.start("later", case.base.prepared().intent)


async def test_shutdown_stops_active_run_and_records_cleanup(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.operation.release.clear()
    result = await case.coordinator.start("start", case.base.prepared().intent)
    await case.preparer.operation.started.wait()
    closed = await case.coordinator.close()
    assert closed.commands == closed.preparations == closed.runs == ()
    assert result.receipt.target_id is not None
    with case.runs.begin() as transaction:
        assert transaction.run(result.receipt.target_id).reason == "runtime_shutdown"
        assert transaction.events(result.receipt.target_id)[-1].event == "run.cleanup"


async def test_timeout_keeps_unresponsive_preparation_owned(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path, preparation=0.02, shutdown=0.02, maximum=1)
    case.preparer.release.clear()
    case.preparer.ignore_cancel = True
    result = await case.coordinator.start("start", case.base.prepared().intent)
    assert result.receipt.reason == "preparation_timeout"
    await case.preparer.cancelled.wait()
    denied = await case.coordinator.start("second", case.base.prepared().intent)
    assert denied.receipt.reason == "preparation_capacity"
    closed = await case.coordinator.close()
    assert closed.preparations == ("start",) and not closed.runs
    case.preparer.release.set()
    await eventually(lambda: not case.coordinator.pending().preparations)
    assert not (await case.coordinator.close()).preparations
    assert not case.preparer.operation.calls


async def test_control_commands_remain_available_when_start_capacity_is_full(
    tmp_path: Path,
) -> None:
    case = coordinator_case(tmp_path, maximum=1)
    case.preparer.release.clear()
    pending = asyncio.create_task(case.coordinator.start("start", case.base.prepared().intent))
    await case.preparer.entered.wait()
    with pytest.raises(CoordinatorUnavailable, match="pending_command_limit"):
        await case.coordinator.start("excess", case.base.prepared().intent)
    result = await case.coordinator.withdraw("start")
    assert result.receipt.disposition == "withdrawn"
    await case.coordinator.close()
    assert (await pending).receipt.disposition == "withdrawn"
