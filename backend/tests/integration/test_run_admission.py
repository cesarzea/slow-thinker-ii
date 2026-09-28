"""Only a saved, funded call can acquire one durable dispatch authorization."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.accounting import BudgetExceeded
from slow_thinker_ii.application import ChargeBasis, RecordingError
from support.authority import PROPOSER, REVIEWER, alias
from support.run_admission import CHARGE, outstanding, run_case


def test_request_tariff_and_reservation_commit_before_dispatch(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(REVIEWER)
    prepared = case.service.reserve(lease.token, '{"prompt":"saved"}', CHARGE)
    assert outstanding(case) == (100, 100, 100)
    with case.store.begin() as transaction:
        assert transaction.call(lease.context.call_id).state == "reserved"
        assert transaction.call(lease.context.call_id).prepared == prepared
        events = transaction.events("run")
        assert [item.sequence for item in events] == [1, 2, 3, 4]
        assert events[-1].event == "call.requested"
        assert lease.token not in repr(events) and lease.token not in repr(prepared)
    assert case.service.authorize(lease.token) == prepared
    with pytest.raises(ValueError, match="only once"):
        case.service.authorize(lease.token)
    with case.store.begin() as transaction:
        assert transaction.call(lease.context.call_id).state == "dispatched"
        assert len(transaction.events("run")) == 5


def test_stop_releases_unsent_calls_and_prevents_dispatch(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(REVIEWER)
    case.service.reserve(lease.token, "{}", CHARGE)
    assert case.service.stop("operator_stop") == (lease.context.call_id,)
    assert outstanding(case) == (0, 0, 0)
    with pytest.raises(AccessDenied):
        case.service.authorize(lease.token)
    with case.store.begin() as transaction:
        assert transaction.call(lease.context.call_id).state == "cancelled"
        assert transaction.run("run").reason == "operator_stop"


def test_stop_preserves_potentially_dispatched_spending(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(REVIEWER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    case.service.stop("operator_stop")
    assert outstanding(case) == (100, 100, 100)
    with case.store.begin() as transaction:
        assert transaction.settle(lease.context.attempt_id, 37, "late-usage") == "applied"
        assert transaction.settle(lease.context.attempt_id, 37, "late-usage") == "duplicate"
        assert transaction.run("run").state == "stopping"
        assert all(scope.settled == 37 for scope in transaction.scopes(case.keys))
    assert outstanding(case) == (0, 0, 0)


def test_budget_denial_stops_run_and_rolls_back_all_scopes(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    first = case.authority.schedule(PROPOSER)
    second = case.authority.schedule(REVIEWER)
    case.service.reserve(first.token, "{}", ChargeBasis(950, "tariff", "{}"))
    with pytest.raises(BudgetExceeded):
        case.service.reserve(second.token, "{}", CHARGE)
    assert outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        assert transaction.run("run").reason == "budget_denied"
        assert transaction.call(first.context.call_id).state == "cancelled"
        with pytest.raises(ValueError, match="Unknown managed call"):
            transaction.call(second.context.call_id)
    with pytest.raises(AccessDenied):
        case.authority.discover(first.token)


def test_failed_evidence_write_rolls_back_money_and_closes_work_authority(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    with case.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken_record BEFORE INSERT ON run_events "
            "WHEN NEW.event='call.requested' BEGIN SELECT RAISE(ABORT,'fixture failure'); END"
        )
    lease = case.authority.schedule(REVIEWER)
    with pytest.raises(RecordingError):
        case.service.reserve(lease.token, "{}", CHARGE)
    assert outstanding(case) == (0, 0, 0)
    with pytest.raises(AccessDenied):
        case.authority.discover(lease.token)
    with case.store.begin() as transaction:
        assert len(transaction.events("run")) == 2


def test_nested_calls_require_their_parent_to_have_dispatch_authority(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    parent = case.authority.schedule(PROPOSER)
    case.service.reserve(parent.token, "{}", None)
    child = case.authority.invoke(parent.token, alias(case.authority, parent.token, REVIEWER))
    with pytest.raises(ValueError, match="originating call"):
        case.service.reserve(child.token, "{}", CHARGE)
    assert outstanding(case) == (0, 0, 0)
    case.service.authorize(parent.token)
    case.service.reserve(child.token, "{}", CHARGE)
    case.service.authorize(child.token)
    assert outstanding(case) == (100, 100, 100)


@pytest.mark.parametrize("payload", ['{"large":"' + "a" * 5000 + '"}', "not-json"])
def test_recording_limits_reject_payload_without_retaining_reservations(
    tmp_path: Path, payload: str
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    with pytest.raises(RecordingError):
        case.service.reserve(lease.token, payload, CHARGE)
    assert outstanding(case) == (0, 0, 0)
