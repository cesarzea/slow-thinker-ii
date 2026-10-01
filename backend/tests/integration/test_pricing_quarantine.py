"""A disproven bound blocks new paid work even when aggregate budgets have room."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.application import CallReceipt
from support.authority import PROPOSER
from support.run_admission import CHARGE, run_case


def test_charge_above_reservation_is_retained_and_quarantined(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    receipt = CallReceipt("reply", lease.context.call_id, "{}", True, amount=150, source="usage")
    outcome = case.service.receive(receipt)
    assert not outcome.publish and outcome.reason == "budget_overrun"
    assert case.service.receive(receipt).settlement == "applied"
    with case.store.begin() as transaction:
        assert transaction.run("run").reason == "budget_overrun"
        assert all(
            scope.settled == 150 and scope.outstanding == 0
            for scope in transaction.scopes(case.keys)
        )
    case.database.initialize()
    with case.database.transaction() as db:
        row = db.execute("SELECT tariff_revision,bound,amount FROM pricing_quarantine").fetchone()
        assert tuple(row) == (CHARGE.tariff_revision, 100, 150)


def test_quarantined_pricing_cannot_reserve_again(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", CHARGE)
    case.service.authorize(lease.token)
    with case.database.transaction() as db:
        db.execute(
            "INSERT INTO pricing_quarantine(tariff_revision,pricing_json,call_id,bound,amount) "
            "VALUES(?,?,?,?,?)",
            (CHARGE.tariff_revision, "{}", lease.context.call_id, 100, 150),
        )
    case.authority.finish(lease.context.call_id, succeeded=True)
    next_call = case.authority.schedule(PROPOSER)
    with pytest.raises(AccessDenied, match="pricing_bound_quarantined"):
        case.service.reserve(next_call.token, "{}", replace(CHARGE, bound=50))
