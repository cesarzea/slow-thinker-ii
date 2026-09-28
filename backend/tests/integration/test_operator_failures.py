"""Receipt failure cannot claim a Stop or create an unrecorded session."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore
from slow_thinker_ii.application import RecordingError
from support.operator_commands import operator_case


@pytest.mark.parametrize("withdrawal", [False, True])
def test_stop_or_withdrawal_receipt_failure_rolls_back_the_gate(
    tmp_path: Path, withdrawal: bool
) -> None:
    case = operator_case(tmp_path)
    receipt = case.store.admit("start", case.prepared()).receipt
    assert receipt.target_id is not None
    table = "operator_withdrawals" if withdrawal else "operator_commands"
    with case.database.transaction() as db:
        db.execute(
            f"CREATE TRIGGER deny BEFORE INSERT ON {table} "
            "BEGIN SELECT RAISE(ABORT,'injected'); END"
        )
    with pytest.raises(RecordingError):
        if withdrawal:
            case.store.withdraw("start")
        else:
            case.store.stop("stop", receipt.target_id)
    with case.database.transaction() as db:
        row = db.execute("SELECT state,reason,event_sequence FROM managed_runs").fetchone()
        assert tuple(row) == ("created", None, 1)
        assert db.execute("SELECT count(*) FROM operator_withdrawals").fetchone()[0] == 0
    assert case.store.command("start") == receipt and case.store.command("stop") is None


def test_session_receipt_failure_leaves_no_partial_scope(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    with case.database.transaction() as db:
        db.execute(
            "CREATE TRIGGER deny BEFORE INSERT ON operator_commands "
            "BEGIN SELECT RAISE(ABORT,'injected'); END"
        )
    with pytest.raises(RecordingError):
        case.store.create_session("another", "Another")
    with case.database.transaction() as db:
        assert db.execute("SELECT count(*) FROM operator_sessions").fetchone()[0] == 1
        assert db.execute("SELECT count(*) FROM budget_scopes").fetchone()[0] == 1


@pytest.mark.parametrize("value", [0, -1, True])
def test_invalid_command_capacity_is_rejected(tmp_path: Path, value: int) -> None:
    case = operator_case(tmp_path)
    with pytest.raises(ValueError):
        SqliteOperatorStore(case.database, value)


def test_malformed_operator_intentions_create_no_receipt(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    with pytest.raises(ValueError):
        case.store.create_session("empty-name", " ")
    with pytest.raises(ValueError):
        case.store.create_session("", "Name")
    with pytest.raises(ValueError):
        case.store.reject("empty-reason", case.prepared().intent, "")
    assert case.store.command("empty-name") is None
    assert case.store.command("empty-reason") is None


@pytest.mark.parametrize("utc", [True, False])
def test_invalid_clock_cannot_admit_a_run(tmp_path: Path, utc: bool) -> None:
    case = operator_case(tmp_path)
    (case.wall if utc else case.clock).value = float("nan")
    with pytest.raises(ValueError):
        case.store.admit("invalid-time", case.prepared())
    assert case.store.command("invalid-time") is None


def test_configuration_payload_bound_retains_previous_configuration(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    bounded = SqliteOperatorStore(case.database, 100, case.clock, case.wall)
    with pytest.raises(RecordingError):
        bounded.configure(case.profile)
    assert case.store.profile() == case.profile
