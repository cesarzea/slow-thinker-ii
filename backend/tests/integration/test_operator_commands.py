"""Lost command replies and concurrent Starts cannot duplicate durable sessions or runs."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path
from threading import Barrier

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import CommandConflict, CommandResult, recover_runs
from slow_thinker_ii.contracts import decode_json, json_object
from support.operator_commands import complete, operator_case


def test_saved_session_and_receipt_survive_restart(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    restarted = SqliteOperatorStore(case.database, 1_048_576, case.clock, case.wall)
    result = restarted.create_session("create-session", "Research")
    assert result.replayed and result.receipt.target_id == case.session_id
    saved = restarted.session(case.session_id)
    assert saved is not None and saved.name == "Research" and saved.created_at == case.wall()
    assert restarted.session("absent") is None and restarted.command("absent") is None
    with pytest.raises(CommandConflict):
        restarted.create_session("create-session", "Different")


@pytest.mark.parametrize("same", [True, False])
def test_simultaneous_starts_admit_one_run(tmp_path: Path, same: bool) -> None:
    case = operator_case(tmp_path)
    barrier = Barrier(2)

    def start(index: int) -> CommandResult:
        barrier.wait()
        return case.store.admit("start" if same else f"start-{index}", case.prepared())

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(start, range(2)))
    assert (
        sum(not item.replayed and item.receipt.disposition == "accepted" for item in results) == 1
    )
    if not same:
        assert any(item.receipt.reason == "active_run_exists" for item in results)
    with case.database.transaction() as db:
        assert db.execute("SELECT count(*) FROM managed_runs").fetchone()[0] == 1
        assert (
            db.execute("SELECT count(*) FROM run_events WHERE event='run.created'").fetchone()[0]
            == 1
        )
        assert db.execute("SELECT count(*) FROM budget_scopes WHERE kind='run'").fetchone()[0] == 1


def test_snapshot_deadline_and_command_conflict(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    prepared = case.prepared()
    receipt = case.store.admit("start", prepared).receipt
    assert receipt.target_id is not None
    with SqliteRunStore(case.database, 1_048_576).begin() as transaction:
        run = transaction.run(receipt.target_id)
        snapshot = json_object(decode_json(run.snapshot_json))
        assert run.deadline == 190 and run.month_id == "2026-09"
        assert snapshot["intent"] == decode_json(prepared.intent.to_json())
        assert snapshot["configuration"] == decode_json(case.profile.to_json())
    changed = replace(prepared, intent=replace(prepared.intent, input_json='{"p":"different"}'))
    with pytest.raises(CommandConflict):
        case.store.admit("start", changed)
    with pytest.raises(CommandConflict):
        case.store.stop("start", receipt.target_id)


def test_rejected_command_never_becomes_a_new_run(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    first = case.store.admit("first", case.prepared()).receipt
    denied = case.store.admit("second", case.prepared()).receipt
    complete(case, first)
    assert case.store.admit("second", case.prepared()).receipt == denied
    accepted = case.store.admit("third", case.prepared())
    assert accepted.receipt.disposition == "accepted" and not accepted.replayed
    assert (
        case.store.reject("third", case.prepared().intent, "now_invalid").receipt
        == accepted.receipt
    )


def test_restart_preserves_start_receipt_and_blocks_unconfirmed_cleanup(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    receipt = case.store.admit("start", case.prepared()).receipt
    assert recover_runs(SqliteRunStore(case.database, 1_048_576)) == (receipt.target_id,)
    restarted = SqliteOperatorStore(case.database, 1_048_576, case.clock, case.wall)
    assert restarted.admit("start", case.prepared()).receipt == receipt
    assert restarted.admit("new", case.prepared()).receipt.reason == "cleanup_unconfirmed"
