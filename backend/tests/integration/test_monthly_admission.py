"""Reservation time determines immutable billing periods, including late settlement."""

from pathlib import Path

import pytest
from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.accounting import BudgetExceeded
from slow_thinker_ii.application import CallReceipt, RecordingError
from slow_thinker_ii.contracts import decode_json, json_object
from support.monthly_admission import monthly_case


def test_crossing_month_preserves_old_obligations_and_common_totals(tmp_path: Path) -> None:
    case = monthly_case(tmp_path)
    old = case.reserve()
    case.move("2026-10-01T00:00:00+00:00")
    new = case.reserve(second=True)
    assert [s.outstanding for s in case.scopes("2026-09")] == [200, 200, 100]
    assert [s.outstanding for s in case.scopes("2026-10")] == [200, 200, 100]
    case.service.stop("operator_stop")
    receipt = CallReceipt("old", old.context.call_id, "{}", True, amount=25, source="usage")
    assert not case.service.receive(receipt).publish
    assert case.service.receive(receipt).disposition == "duplicate"
    case.service.receive(
        CallReceipt("new", new.context.call_id, "{}", True, amount=40, source="usage")
    )
    assert [s.settled for s in case.scopes("2026-09")] == [65, 65, 25]
    assert [s.settled for s in case.scopes("2026-10")] == [65, 65, 40]
    assert all(s.outstanding == 0 for s in case.scopes("2026-10"))


def test_new_month_does_not_reset_run_budget(tmp_path: Path) -> None:
    case = monthly_case(tmp_path)
    case.reserve(bound=950)
    case.move("2026-10-01T00:00:00+00:00")
    with pytest.raises(BudgetExceeded) as denied:
        case.reserve(second=True)
    assert denied.value.scope.kind == "run"
    assert [s.outstanding for s in case.scopes("2026-10")] == [950, 950, 0]
    with case.store.begin() as tx:
        assert tx.run(case.run.run_id).reason == "budget_denied"


def test_overrun_checks_new_attempt_month_not_run_admission_month(tmp_path: Path) -> None:
    case = monthly_case(tmp_path)
    case.move("2026-10-01T00:00:00+00:00")
    lease = case.reserve()
    with case.operator.database.transaction() as db:
        db.execute("UPDATE budget_scopes SET cap=100 WHERE kind='month' AND scope_id='2026-10'")
    result = case.service.receive(
        CallReceipt("overrun", lease.context.call_id, "{}", True, amount=150, source="usage")
    )
    assert result.reason == "budget_overrun" and not result.publish
    assert case.scopes("2026-10")[2].settled == 150
    assert case.scopes("2026-09")[2].settled == 0


@pytest.mark.parametrize(
    "start,end",
    [
        ("2026-12-31T23:59:59+00:00", "2027-01-01T00:00:00+00:00"),
        ("2028-02-29T23:59:59+00:00", "2028-03-01T00:00:00+00:00"),
    ],
)
def test_evidence_records_exact_utc_interval_and_policy(
    tmp_path: Path, start: str, end: str
) -> None:
    case = monthly_case(tmp_path, start)
    lease = case.reserve()
    with case.store.begin() as tx:
        events = [e for e in tx.events(case.run.run_id) if e.event == "accounting.reserved"]
    saved = json_object(decode_json(events[0].payload_json))
    assert saved["attempt_id"] == lease.context.attempt_id
    assert saved["period_start"] == start[:7] + "-01T00:00:00+00:00"
    assert saved["period_end"] == end
    assert saved["timezone"] == "UTC"
    assert saved["admitted_policy_revision"] == case.operator.profile.revision


@pytest.mark.parametrize("value", ["2026-09-30T23:59:59+00:00", "2026-10-01T00:00:00+00:00"])
def test_regressed_clock_closes_admission_without_moving_obligations(
    tmp_path: Path, value: str
) -> None:
    case = monthly_case(tmp_path)
    case.move("2026-10-01T00:00:01+00:00")
    case.reserve()
    case.move(value)
    with pytest.raises(AccessDenied, match="clock_regressed"):
        case.reserve(second=True)
    assert [s.outstanding for s in case.scopes("2026-10")] == [100, 100, 100]
    with case.store.begin() as tx:
        assert tx.run(case.run.run_id).reason == "clock_regressed"


def test_failed_call_record_rolls_back_new_month_and_clock_watermark(tmp_path: Path) -> None:
    case = monthly_case(tmp_path)
    original = case.operator.wall.value
    case.move("2026-10-01T00:00:00+00:00")
    with case.operator.database.transaction() as db:
        db.execute(
            "CREATE TRIGGER broken BEFORE INSERT ON run_events WHEN NEW.event='call.requested' "
            "BEGIN SELECT RAISE(ABORT,'fixture'); END"
        )
    with pytest.raises(RecordingError):
        case.reserve()
    with case.operator.database.transaction() as db:
        assert db.execute("SELECT count(*) FROM spending_attempts").fetchone()[0] == 0
        assert (
            db.execute("SELECT count(*) FROM budget_scopes WHERE scope_id='2026-10'").fetchone()[0]
            == 0
        )
        assert (
            db.execute("SELECT last_admitted_at FROM operator_workspace").fetchone()[0] == original
        )
