"""The runner connects authority, durable admission and result settlement around a single call."""

import asyncio
from pathlib import Path

import pytest
from slow_thinker_ii.accounting import BudgetExceeded
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence, ManagedCalls
from support.authority import PROPOSER, REVIEWER
from support.managed_calls import FixtureOperation, NestedOperation, RealClock
from support.run_admission import CHARGE, outstanding, run_case


async def test_runner_records_and_settles_a_call_before_returning_it(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE, ChargeEvidence('{"tokens":7}', 37, "usage"))
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    result = await runner.schedule(PROPOSER, '{"input":1}')
    assert result.outcome.publish and result.result.payload_json == '{"done":true}'
    assert len(operation.calls) == 1 and not runner.pending()
    assert outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        assert transaction.call(result.context.call_id).state == "completed"
        assert transaction.receipt(result.receipt_id) is not None
        assert all(scope.settled == 37 for scope in transaction.scopes(case.keys))
    pending = await runner.close(1)
    assert pending == ()


async def test_nested_calls_progress_and_only_the_leaf_is_charged(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    parent = NestedOperation(case)
    child = FixtureOperation(CHARGE, ChargeEvidence('{"tokens":7}', 37, "usage"))
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: parent, REVIEWER: child})
    parent.runner = runner
    result = await runner.schedule(PROPOSER, "{}")
    assert result.outcome.publish and parent.child is not None
    assert parent.child.context.parent_call_id == result.context.call_id
    assert parent.child.context.caller == "proposer"
    assert parent.child.context.deadline <= result.context.deadline
    with case.store.begin() as transaction:
        assert all(scope.settled == 37 for scope in transaction.scopes(case.keys))
        assert (
            sum(event.event == "call.dispatch_authorized" for event in transaction.events("run"))
            == 2
        )


@pytest.mark.parametrize("bound", [None, 2000])
async def test_rejection_never_reaches_the_transport(tmp_path: Path, bound: int | None) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(None if bound is None else ChargeBasis(bound, "tariff", "{}"))
    operation.reject = bound is None
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    with pytest.raises(ValueError if bound is None else BudgetExceeded):
        await runner.schedule(PROPOSER, "{}")
    assert not operation.calls and not runner.pending()
    with case.store.begin() as transaction:
        assert any(event.event == "call.rejected" for event in transaction.events("run"))


async def test_transport_error_is_recorded_without_repeating_or_releasing_charge(
    tmp_path: Path,
) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE)
    operation.error = RuntimeError("fixture secret diagnostic")
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    result = await runner.schedule(PROPOSER, "{}")
    assert result.result.is_error and not result.outcome.publish
    assert "RuntimeError" in result.result.payload_json
    assert "secret" not in result.result.payload_json
    assert len(operation.calls) == 1 and outstanding(case) == (100, 100, 100)


async def test_stop_cancels_active_calls_and_preserves_uncertain_cost(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite", clock=RealClock())
    operation = FixtureOperation(CHARGE)
    operation.release.clear()
    runner = ManagedCalls(case.authority, case.service, {PROPOSER: operation})
    task = asyncio.create_task(runner.schedule(PROPOSER, "{}"))
    await asyncio.wait_for(operation.started.wait(), 2)
    pending = runner.pending()
    assert runner.stop("operator_stop") == (pending[0].call_id,)
    with pytest.raises(asyncio.CancelledError):
        await task
    assert not runner.pending() and outstanding(case) == (100, 100, 100)
    with case.store.begin() as transaction:
        assert transaction.call(pending[0].call_id).state == "cancelled"
