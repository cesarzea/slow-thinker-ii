"""Response evidence, settlement and publication commit together without duplicate work."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import CallReceipt
from support.authority import PROPOSER, REVIEWER, alias
from support.run_admission import CHARGE, outstanding, run_case


def test_receipt_persists_native_evidence_and_settles_once(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    receipt = CallReceipt(
        "reply", lease.context.call_id, '{"native":" ñ "}', True, '{"tokens":7}', 37, "usage"
    )
    outcome = case.service.receive(receipt)
    assert outcome.publish and outcome.settlement == "applied"
    assert outstanding(case) == (0, 0, 0)
    with case.store.begin() as transaction:
        saved = transaction.receipt("reply")
        assert saved is not None and saved.receipt == receipt and saved.outcome == outcome
        assert transaction.call(lease.context.call_id).state == "completed"
        assert all(scope.settled == 37 for scope in transaction.scopes(case.keys))
        events = transaction.events("run")
        assert [item.event for item in events[-4:]] == [
            "call.response_received",
            "usage.recorded",
            "accounting.changed",
            "call.finished",
        ]
    duplicate = case.service.receive(receipt)
    assert not duplicate.publish and duplicate.disposition == "duplicate"
    with case.store.begin() as transaction:
        assert transaction.events("run") == events
    with pytest.raises(AccessDenied):
        case.authority.context(lease.token)


def test_conflicting_receipt_cannot_replace_response_or_charge(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    original = CallReceipt(
        "reply", lease.context.call_id, '"original"', True, amount=37, source="usage"
    )
    case.service.receive(original)
    outcome = case.service.receive(replace(original, response_json='"changed"', amount=75))
    assert outcome.disposition == "conflict" and not outcome.publish
    with case.store.begin() as transaction:
        saved = transaction.receipt("reply")
        assert saved is not None and saved.receipt == original
        assert all(scope.settled == 37 for scope in transaction.scopes(case.keys))
        assert '"conflict": true' in transaction.events("run")[-1].payload_json


def test_missing_usage_retains_obligation_until_later_evidence(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    receipt = CallReceipt("first", lease.context.call_id, '"answer"', True)
    assert case.service.receive(receipt).publish
    assert outstanding(case) == (100, 100, 100)
    later = replace(
        receipt, receipt_id="usage-arrival", usage_json='{"tokens":7}', amount=37, source="usage"
    )
    outcome = case.service.receive(later)
    assert not outcome.publish and outcome.reason == "late_response"
    assert outcome.settlement == "applied" and outstanding(case) == (0, 0, 0)
    with case.database.transaction() as connection:
        assert (
            connection.execute("SELECT result_receipt_id FROM managed_calls").fetchone()[0]
            == "first"
        )


@pytest.mark.parametrize("sent", [False, True])
def test_parent_cannot_publish_with_active_children_and_unsent_reservations_are_released(
    tmp_path: Path,
    sent: bool,
) -> None:
    case = run_case(tmp_path / "run.sqlite")
    parent = case.authority.schedule(PROPOSER)
    case.service.reserve(parent.token, "{}", None)
    case.service.authorize(parent.token)
    child = case.authority.invoke(parent.token, alias(case.authority, parent.token, REVIEWER))
    case.service.reserve(child.token, "{}", CHARGE)
    if sent:
        case.service.authorize(child.token)
    outcome = case.service.receive(
        CallReceipt("reply", parent.context.call_id, '"premature"', True)
    )
    assert not outcome.publish and outcome.reason == "unfinished_children"
    assert outstanding(case) == ((100, 100, 100) if sent else (0, 0, 0))
    with case.store.begin() as transaction:
        assert transaction.call(parent.context.call_id).state == "failed"
        assert transaction.call(child.context.call_id).state == "cancelled"
    with pytest.raises(AccessDenied):
        case.authority.context(child.token)


def test_billed_operation_failure_retains_response_and_cost(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    outcome = case.service.receive(
        CallReceipt(
            "error", lease.context.call_id, '{"error":"refusal"}', False, amount=12, source="usage"
        )
    )
    assert not outcome.publish and outcome.reason == "operation_failed"
    assert outcome.settlement == "applied"
    with case.store.begin() as transaction:
        assert transaction.call(lease.context.call_id).state == "failed"
        assert all(scope.settled == 12 for scope in transaction.scopes(case.keys))
