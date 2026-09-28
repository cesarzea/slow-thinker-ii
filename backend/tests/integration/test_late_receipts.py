"""Late evidence may settle money but cannot revive work or overwrite outcomes."""

from pathlib import Path

import pytest
from slow_thinker_ii.application import CallReceipt, RecordingError, recover_runs
from support.authority import PROPOSER
from support.run_admission import CHARGE, outstanding, run_case


@pytest.mark.parametrize("recover", [False, True])
def test_receipt_after_stop_or_recovery_only_records_and_settles(
    tmp_path: Path, recover: bool
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    case.service.stop("operator_stop")
    if recover:
        recover_runs(case.store)
    result = case.service.receive(
        CallReceipt(
            "late", lease.context.call_id, '"late answer"', True, amount=25, source="late-usage"
        )
    )
    assert not result.publish and result.settlement == "applied"
    with case.store.begin() as transaction:
        assert transaction.call(lease.context.call_id).state == ("cancelled")
        assert transaction.run("run").state == ("interrupted" if recover else "stopping")
        assert transaction.run("run").reason == "operator_stop"
        assert '"late": true' in transaction.events("run")[-1].payload_json


def test_deadline_expiry_prevents_publication_but_not_settlement(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    case.clock.now = lease.context.deadline
    result = case.service.receive(
        CallReceipt("late", lease.context.call_id, '"answer"', True, amount=25, source="usage")
    )
    assert result.reason == "deadline_expired" and not result.publish
    with case.store.begin() as transaction:
        assert transaction.run("run").state == "stopping"
        assert transaction.call(lease.context.call_id).state == "failed"
        assert all(scope.settled == 25 for scope in transaction.scopes(case.keys))


def test_charge_above_budget_is_recorded_in_full_and_closes_run(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    result = case.service.receive(
        CallReceipt(
            "overrun",
            lease.context.call_id,
            '"answer"',
            True,
            amount=1200,
            source="reported-charge",
        )
    )
    assert result.reason == "budget_overrun" and not result.publish
    with case.store.begin() as transaction:
        assert transaction.run("run").reason == "budget_overrun"
        assert all(scope.settled == 1200 for scope in transaction.scopes(case.keys))


def test_result_write_failure_rolls_back_response_and_money_together(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    with case.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken_result BEFORE INSERT ON run_events "
            "WHEN NEW.event='usage.recorded' BEGIN SELECT RAISE(ABORT,'failed'); END"
        )
    receipt = CallReceipt(
        "reply", lease.context.call_id, '"answer"', True, '{"tokens":7}', 25, "usage"
    )
    with pytest.raises(RecordingError):
        case.service.receive(receipt)
    assert outstanding(case) == (100, 100, 100)
    with case.store.begin() as transaction:
        assert transaction.receipt("reply") is None
        assert transaction.call(lease.context.call_id).state == "dispatched"
        assert all(scope.settled == 0 for scope in transaction.scopes(case.keys))
