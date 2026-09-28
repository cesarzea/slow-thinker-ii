"""Failed preparation or expired authorization must never become external work."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import ManagedCalls, RecordingError
from support.authority import PROPOSER, Clock
from support.managed_calls import FixtureOperation, RealClock
from support.run_admission import CHARGE, outstanding, run_case


async def test_expiry_between_reservation_and_dispatch_releases_unsent_money(
    tmp_path: Path,
) -> None:
    clock = Clock()
    case = run_case(tmp_path / "run.sqlite", clock=clock)
    operation = FixtureOperation(CHARGE)
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    task = asyncio.create_task(runner.schedule(PROPOSER, "{}"))
    asyncio.get_running_loop().call_soon(setattr, clock, "now", 100)
    with pytest.raises(AccessDenied):
        await task
    assert not operation.calls and not runner.pending()
    assert outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        assert any(event.event == "call.cancel_requested" for event in transaction.events("run"))


async def test_preparation_failure_is_recorded_without_private_exception_text(
    tmp_path: Path,
) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE)
    operation.preparation_error = RuntimeError("private quote diagnostic")
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    with pytest.raises(RuntimeError, match="private quote"):
        await runner.schedule(PROPOSER, "{}")
    assert not operation.calls and outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        rejected = [event for event in transaction.events("run") if event.event == "call.rejected"]
        assert len(rejected) == 1
        assert "operation_preparation_failed" in rejected[0].payload_json
        assert "private" not in rejected[0].payload_json


async def test_failed_durable_authorization_never_reaches_process(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE)
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    with case.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken_dispatch BEFORE UPDATE ON spending_attempts "
            "WHEN NEW.state='dispatched' BEGIN SELECT RAISE(ABORT,'fixture failure'); END"
        )
    with pytest.raises(RecordingError):
        await runner.schedule(PROPOSER, "{}")
    assert not operation.calls and not runner.pending()
    with pytest.raises(AccessDenied):
        case.authority.schedule(PROPOSER)
    assert outstanding(case) == (100, 100, 100)
    assert await runner.close(1) == ()
    assert outstanding(case) == (0, 0, 0)
