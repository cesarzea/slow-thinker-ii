"""Durable Stop and withdrawal reach the owned runtime, not just its database record."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.application import PreparationRejected, RecordingError
from support.coordinator import coordinator_case, eventually


@pytest.mark.parametrize("withdrawal", [False, True])
async def test_stop_and_withdrawal_cancel_business_work(tmp_path: Path, withdrawal: bool) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.operation.release.clear()
    result = await case.coordinator.start("start", case.base.prepared().intent)
    await case.preparer.operation.started.wait()
    identity = result.receipt.target_id
    assert identity is not None
    stopped = await (
        case.coordinator.withdraw("start")
        if withdrawal
        else case.coordinator.stop("stop", identity)
    )
    assert stopped.receipt.target_id == identity
    await eventually(lambda: not case.coordinator.pending().runs)
    with case.runs.begin() as transaction:
        assert transaction.run(identity).state == "cancelled"
        assert transaction.run(identity).reason == "operator_stop"
        assert transaction.events(identity)[-1].event == "run.cleanup"
    assert not case.coordinator.failures()
    await case.coordinator.close()


async def test_withdraw_during_preparation_prevents_all_business_calls(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.release.clear()
    request = asyncio.create_task(case.coordinator.start("start", case.base.prepared().intent))
    await case.preparer.entered.wait()
    withdrawn = await case.coordinator.withdraw("start")
    case.preparer.release.set()
    assert (await request).receipt == withdrawn.receipt
    assert not case.preparer.operation.calls and not case.coordinator.pending().runs
    await case.coordinator.close()


@pytest.mark.parametrize("withdrawal", [False, True])
async def test_receipt_storage_failure_revokes_live_authority(
    tmp_path: Path, withdrawal: bool
) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.operation.release.clear()
    result = await case.coordinator.start("start", case.base.prepared().intent)
    await case.preparer.operation.started.wait()
    table = "operator_withdrawals" if withdrawal else "operator_commands"
    with case.base.database.transaction() as db:
        db.execute(
            f"CREATE TRIGGER deny BEFORE INSERT ON {table} "
            "BEGIN SELECT RAISE(ABORT,'injected'); END"
        )
    assert result.receipt.target_id is not None
    with pytest.raises(RecordingError):
        if withdrawal:
            await case.coordinator.withdraw("start")
        else:
            await case.coordinator.stop("stop", result.receipt.target_id)
    await eventually(lambda: not case.coordinator.pending().runs)
    with case.runs.begin() as transaction:
        assert transaction.run(result.receipt.target_id).reason == "recording_failure"
    await case.coordinator.close()


async def test_known_preflight_rejection_is_durable(tmp_path: Path) -> None:
    case = coordinator_case(tmp_path)
    case.preparer.failure = PreparationRejected("invalid_graph")
    result = await case.coordinator.start("start", case.base.prepared().intent)
    assert result.receipt.reason == "invalid_graph"
    case.preparer.failure = None
    assert (await case.coordinator.start("start", case.base.prepared().intent)).replayed
    assert len(case.preparer.calls) == 1
    await case.coordinator.close()
