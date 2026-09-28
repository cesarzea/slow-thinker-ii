"""A command has one owner across retries, lost waiters and backend receipt recovery."""

import asyncio
from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.application import CommandConflict, ExecutionCoordinator, PreparationRejected
from support.coordinator import coordinator_case, eventually
from support.managed_calls import RealClock


async def test_simultaneous_duplicate_commands_execute_once(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    intent = case.base.prepared().intent
    first, duplicate = await asyncio.gather(
        case.coordinator.start("start", intent), case.coordinator.start("start", intent)
    )
    assert first.receipt == duplicate.receipt and duplicate.replayed
    await eventually(lambda: not case.coordinator.pending().runs)
    assert len(case.preparer.calls) == len(case.preparer.operation.calls) == 1
    assert first.receipt.target_id is not None
    with case.runs.begin() as transaction:
        assert transaction.run(first.receipt.target_id).state == "completed"
    assert case.coordinator.failures() == ()
    assert not (await case.coordinator.close()).runs


async def test_lost_waiter_does_not_cancel_command_or_duplicate_execution(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.release.clear()
    intent = case.base.prepared().intent
    waiter = asyncio.create_task(case.coordinator.start("start", intent))
    await case.preparer.entered.wait()
    waiter.cancel()
    with pytest.raises(asyncio.CancelledError):
        await waiter
    assert not case.preparer.cancelled.is_set()
    case.preparer.release.set()
    replay = await case.coordinator.start("start", intent)
    await eventually(lambda: not case.coordinator.pending().runs)
    assert replay.replayed and len(case.preparer.operation.calls) == 1
    await case.coordinator.close()


async def test_pending_command_rejects_changed_content(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.release.clear()
    intent = case.base.prepared().intent
    pending = asyncio.create_task(case.coordinator.start("start", intent))
    await case.preparer.entered.wait()
    with pytest.raises(CommandConflict):
        await case.coordinator.start("start", replace(intent, input_json='{"changed":true}'))
    await case.coordinator.close()
    assert (await pending).receipt.disposition == "rejected"


async def test_receipt_replay_never_prepares_or_launches_again(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    intent = case.base.prepared().intent
    original = await case.coordinator.start("start", intent)
    await eventually(lambda: not case.coordinator.pending().runs)
    await case.coordinator.close()
    case.preparer.failure = PreparationRejected("removed_installation")
    fresh = ExecutionCoordinator(case.commands, case.runs, case.preparer, RealClock(), 5, 2, 4)
    replay = await fresh.start("start", intent)
    assert replay.replayed and replay.receipt == original.receipt
    assert len(case.preparer.calls) == 1 and fresh.pending().runs == ()
    await fresh.close()
