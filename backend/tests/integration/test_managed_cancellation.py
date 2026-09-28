"""Deadlines and cancellation retain execution ownership and uncertain obligations."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.application import ManagedCalls
from support.authority import PROPOSER
from support.managed_calls import FixtureOperation, RealClock
from support.run_admission import CHARGE, outstanding, run_case


async def test_call_deadline_records_failure_and_preserves_reservation(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock(), seconds=0.05)
    operation = FixtureOperation(CHARGE)
    operation.release.clear()
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    result = await asyncio.wait_for(runner.schedule(PROPOSER, "{}"), 2)
    assert "call_deadline" in result.result.payload_json
    assert not result.outcome.publish and not runner.pending()
    assert outstanding(case) == (100, 100, 100)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "stopping"
        assert transaction.run("run").reason == "deadline_expired"


async def test_stop_before_dispatch_releases_reservation_without_sending(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE)
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    task = asyncio.create_task(runner.schedule(PROPOSER, "{}"))
    asyncio.get_running_loop().call_soon(runner.stop, "operator_stop")
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not operation.calls and not runner.pending()
    assert outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        events = transaction.events("run")
        assert any(event.event == "call.cancel_requested" for event in events)
        assert all(event.event != "call.dispatch_authorized" for event in events)


async def test_cleanup_reports_stubborn_work_until_it_actually_finishes(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE)
    operation.ignore_cancel = True
    operation.release.clear()
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    task = asyncio.create_task(runner.schedule(PROPOSER, "{}"))
    await asyncio.wait_for(operation.started.wait(), 2)
    try:
        pending = await asyncio.wait_for(runner.close(0.01), 2)
        assert len(pending) == 1 and pending == runner.pending()
        assert case.authority.stop() == (pending[0].call_id,)
        assert outstanding(case) == (100, 100, 100)
    finally:
        operation.release.set()
        result = await asyncio.wait_for(task, 2)
    assert not result.outcome.publish and not runner.pending()
    assert not case.authority.stop()


@pytest.mark.parametrize("timeout", [0, -1, float("nan"), float("inf"), True])
async def test_invalid_cleanup_bound_does_not_stop_the_run(tmp_path: Path, timeout: float) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    runner = ManagedCalls(case.authority, case.service, {})
    with pytest.raises(ValueError, match="positive finite"):
        await runner.close(timeout)
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "running"


async def test_unknown_operation_binding_is_rejected_and_releases_occupancy(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    runner = ManagedCalls(case.authority, case.service, {})
    with pytest.raises(ValueError, match="No ready operation"):
        await runner.schedule(PROPOSER, "{}")
    lease = case.authority.schedule(PROPOSER)
    assert lease.context.target == PROPOSER
    assert outstanding(case) == (0, 0, 0)
