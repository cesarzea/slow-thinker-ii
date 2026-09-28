"""Higher-scope policies can constrain a running graph without granting it new limits."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.accounting import BudgetExceeded
from slow_thinker_ii.adapters.sqlite import SqliteOperatorQueries
from slow_thinker_ii.contracts import decode_json, json_object
from support.authority import PROPOSER
from support.monthly_admission import configure, monthly_case


@pytest.mark.parametrize("scope", ["session", "month"])
def test_raised_policy_does_not_increase_running_graph_ceiling(tmp_path: Path, scope: str) -> None:
    case = monthly_case(tmp_path)
    case.move("2026-10-01T00:00:00+00:00")
    configure(case, session=20000, month=30000)
    with case.operator.database.transaction() as db:
        if scope == "month":
            db.execute(
                "INSERT INTO budget_scopes(kind,scope_id,cap,settled) "
                "VALUES('month','2026-10',30000,9950)"
            )
        else:
            db.execute("UPDATE budget_scopes SET settled=4950 WHERE kind='session'")
    with pytest.raises(BudgetExceeded) as denied:
        case.reserve()
    assert denied.value.scope.kind == scope
    assert denied.value.scope.cap == (5000 if scope == "session" else 10000)
    assert case.scopes("2026-10")[2].cap == 30000


@pytest.mark.parametrize("scope", ["session", "month"])
def test_lower_current_limits_apply_to_next_call(tmp_path: Path, scope: str) -> None:
    case = monthly_case(tmp_path)
    case.reserve()
    case.move("2026-10-01T00:00:00+00:00")
    configure(
        case, session=150 if scope == "session" else 5000, month=0 if scope == "month" else 10000
    )
    with pytest.raises(BudgetExceeded) as denied:
        case.reserve(second=True)
    assert denied.value.scope.kind == scope
    assert case.scopes("2026-09")[2].outstanding == 100
    assert case.scopes("2026-10")[2].outstanding == 0


@pytest.mark.parametrize("invalid", [float("nan"), float("inf"), -1.0, 1e100, True])
def test_invalid_wall_clock_prevents_paid_dispatch(tmp_path: Path, invalid: float) -> None:
    case = monthly_case(tmp_path)
    case.operator.wall.value = invalid
    with pytest.raises(AccessDenied, match="invalid_clock"):
        case.reserve()
    with case.store.begin() as tx:
        assert tx.run(case.run.run_id).reason == "invalid_clock"
    assert all(s.outstanding == 0 for s in case.scopes("2026-09"))


def test_unpriced_calls_do_not_create_a_monthly_obligation(tmp_path: Path) -> None:
    case = monthly_case(tmp_path)
    case.operator.wall.value = float("nan")
    lease = case.authority.schedule(PROPOSER)
    case.service.reserve(lease.token, "{}", None)
    case.service.authorize(lease.token)
    with case.operator.database.transaction() as db:
        assert db.execute("SELECT count(*) FROM spending_attempts").fetchone()[0] == 0


def test_inspector_and_workspace_show_the_actual_attempt_period(tmp_path: Path) -> None:
    case = monthly_case(tmp_path)
    old = case.reserve()
    case.move("2026-10-01T00:00:00+00:00")
    new = case.reserve(second=True)
    queries = SqliteOperatorQueries(case.operator.database, b"q" * 32, wall=case.operator.wall)
    for lease, month in ((old, "2026-09"), (new, "2026-10")):
        encoded = queries.call(case.run.run_id, lease.context.call_id)
        assert encoded is not None
        details = json_object(decode_json(encoded))
        assert json_object(details["accounting"])["month_id"] == month
    workspace = json_object(decode_json(queries.workspace()))
    current = json_object(workspace["month_budget"])
    assert current["scope_id"] == "2026-10"
    assert current["outstanding"] == "0.000000100"
