"""Invalid receipts cannot settle unsent work or replace recorded identities."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.application import CallReceipt
from support.authority import PROPOSER
from support.run_admission import CHARGE, run_case


def test_unsent_call_cannot_receive_a_response_or_settlement(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    with pytest.raises(ValueError, match="prior dispatch"):
        case.service.receive(
            CallReceipt("reply", lease.context.call_id, "{}", True, amount=25, source="usage")
        )
    assert case.authority.context(lease.token) == lease.context


def test_unbilled_call_can_complete_but_cannot_duplicate_a_child_charge(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", None)
    case.service.authorize(lease.token)
    receipt = CallReceipt("reply", lease.context.call_id, "{}", True)
    with pytest.raises(ValueError, match="unbilled"):
        case.service.receive(replace(receipt, amount=25, source="child-charge"))
    assert case.service.receive(receipt).publish


def test_later_conflicting_usage_preserves_original_settlement(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    receipt = CallReceipt("reply", lease.context.call_id, "{}", True, amount=25, source="usage")
    case.service.receive(receipt)
    outcome = case.service.receive(replace(receipt, receipt_id="later", amount=30))
    assert not outcome.publish and outcome.settlement == "conflict"
    with case.store.begin() as transaction:
        assert all(scope.settled == 25 for scope in transaction.scopes(case.keys))
        assert transaction.receipt("later") is not None


@pytest.mark.parametrize("amount,source", [(-1, "usage"), (True, "usage"), (25, "")])
def test_receipt_rejects_invalid_amounts_or_missing_evidence(amount: int, source: str) -> None:
    with pytest.raises(ValueError, match="source evidence"):
        CallReceipt("reply", "call", "{}", True, amount=amount, source=source)


def test_receipt_identities_are_required() -> None:
    with pytest.raises(ValueError, match="identities"):
        CallReceipt("", "call", "{}", True)
