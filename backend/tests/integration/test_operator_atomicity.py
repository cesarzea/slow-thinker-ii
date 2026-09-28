"""Failed command persistence leaves no run, event, partial scope or success receipt."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import RecordingError
from slow_thinker_ii.contracts import encode_json
from support.operator_commands import complete, operator_case


@pytest.mark.parametrize(
    "table", ["operator_commands", "operator_runs", "run_events", "budget_scopes"]
)
def test_partial_admission_rolls_back_every_effect(tmp_path: Path, table: str) -> None:
    case = operator_case(tmp_path)
    with case.database.transaction() as db:
        db.execute(
            f"CREATE TRIGGER deny_write BEFORE INSERT ON {table} "
            "BEGIN SELECT RAISE(ABORT,'injected'); END"
        )
    with pytest.raises(RecordingError):
        case.store.admit("start", case.prepared())
    with case.database.transaction() as db:
        for name in ("managed_runs", "operator_runs", "run_events"):
            assert db.execute(f"SELECT count(*) FROM {name}").fetchone()[0] == 0
        assert (
            db.execute("SELECT count(*) FROM budget_scopes WHERE kind!='session'").fetchone()[0]
            == 0
        )
        assert db.execute("SELECT last_admitted_at FROM operator_workspace").fetchone()[0] is None
    assert case.store.command("start") is None


def test_oversized_snapshot_never_creates_a_receipt(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    bounded = SqliteOperatorStore(case.database, 100, case.clock, case.wall)
    with pytest.raises(RecordingError):
        bounded.admit("start", case.prepared())
    assert bounded.command("start") is None


@pytest.mark.parametrize(
    "report",
    [
        "{}",
        '{"pending_calls":["call"],"environment_json":"[]"}',
        '{"pending_calls":[],"environment_json":false}',
        '{"pending_calls":[],"environment_json":"{}"}',
        '{"pending_calls":[],"environment_json":"[{}]"}',
    ],
)
def test_unconfirmed_cleanup_keeps_new_starts_blocked(tmp_path: Path, report: str) -> None:
    case = operator_case(tmp_path)
    original = case.store.admit("start", case.prepared()).receipt
    complete(case, original, cleanup=False)
    assert original.target_id is not None
    with SqliteRunStore(case.database, 1_048_576).begin() as transaction:
        transaction.event(original.target_id, "run.cleanup", None, report)
    assert case.store.admit("next", case.prepared()).receipt.reason == "cleanup_unconfirmed"
    with SqliteRunStore(case.database, 1_048_576).begin() as transaction:
        transaction.event(
            original.target_id,
            "run.cleanup",
            None,
            encode_json({"pending_calls": [], "environment_json": '[{"status":"stopped"}]'}),
        )
    assert case.store.admit("corrected", case.prepared()).receipt.disposition == "accepted"
