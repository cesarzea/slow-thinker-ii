"""Withdrawal tombstones and Stop receipts serialize against in-flight Start intentions."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteRunStore
from slow_thinker_ii.application import CommandConflict, CommandResult
from support.operator_commands import complete, operator_case


def test_withdraw_before_start_never_creates_work(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    result = case.store.withdraw("unknown")
    assert result.receipt.disposition == "withdrawn" and not result.replayed
    assert case.store.withdraw("unknown").replayed
    assert case.store.admit("unknown", case.prepared()).receipt == result.receipt
    with case.database.transaction() as db:
        assert db.execute("SELECT count(*) FROM managed_runs").fetchone()[0] == 0
    with pytest.raises(CommandConflict):
        case.store.withdraw("create-session")


def test_simultaneous_start_and_withdrawal_cannot_leave_admission_open(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    barrier = Barrier(2)

    def command(start: bool) -> CommandResult:
        barrier.wait()
        return case.store.admit("start", case.prepared()) if start else case.store.withdraw("start")

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(command, (True, False)))
    assert results[1].receipt.disposition == "withdrawn"
    with case.database.transaction() as db:
        rows = db.execute("SELECT state,reason FROM managed_runs").fetchall()
        assert len(rows) <= 1
        assert all(tuple(row) == ("stopping", "operator_stop") for row in rows)
    assert case.store.admit("start", case.prepared()).replayed


def test_withdraw_accepted_start_preserves_original_receipt(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    original = case.store.admit("start", case.prepared()).receipt
    withdrawal = case.store.withdraw("start").receipt
    assert withdrawal.target_id == original.target_id and withdrawal.reason == "operator_stop"
    assert case.store.command("start") == original
    assert case.store.withdraw("start").receipt == withdrawal


def test_stop_deadline_primary_reason_and_terminal_replay(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    original = case.store.admit("start", case.prepared()).receipt
    assert original.target_id is not None
    case.clock.value = 200
    stopped = case.store.stop("stop", original.target_id)
    assert stopped.receipt.reason == "run_deadline"
    case.clock.value = 150
    assert case.store.stop("stop", original.target_id).replayed
    assert case.store.stop("another", original.target_id).receipt.reason == "run_deadline"
    with SqliteRunStore(case.database, 1_048_576).begin() as transaction:
        transaction.finish_run(original.target_id, "runtime", 200, None, executing=False)
    assert case.store.stop("terminal", original.target_id).receipt.disposition == "already_terminal"
    assert case.store.stop("stop", original.target_id).receipt == stopped.receipt


def test_stop_unknown_and_withdraw_terminal_or_rejected(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    assert case.store.stop("unknown", "missing").receipt.reason == "unknown_run"
    rejected = case.store.reject("invalid", case.prepared().intent, "invalid_graph")
    assert case.store.withdraw("invalid").receipt.disposition == "withdrawn"
    assert case.store.command("invalid") == rejected.receipt
    original = case.store.admit("start", case.prepared()).receipt
    complete(case, original)
    assert case.store.withdraw("start").receipt.disposition == "withdrawn"
