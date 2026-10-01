"""Durable launch intents are atomic and block new admission until ownership is resolved."""

import sqlite3
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteProcessJournal
from slow_thinker_ii.application import OwnedLaunch
from support.operator_commands import complete, operator_case
from support.run_admission import run_case


def test_pending_ownership_blocks_even_a_confirmed_old_cleanup(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    receipt = case.store.admit("first", case.prepared()).receipt
    assert receipt.target_id is not None
    journal = SqliteProcessJournal(case.database, 4096)
    journal.prepare(OwnedLaunch("owned", receipt.target_id, "runtime", "worker", str(tmp_path)))
    complete(case, receipt)
    assert case.store.admit("blocked", case.prepared()).receipt.reason == "cleanup_unconfirmed"
    journal.stopped("owned", "verified_absent")
    assert case.store.admit("next", case.prepared()).receipt.disposition == "accepted"


def test_failed_launch_event_leaves_no_unrecorded_partial_intention(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    with case.database.transaction() as db:
        db.execute(
            "CREATE TRIGGER fail_host BEFORE INSERT ON run_events "
            "WHEN NEW.event='host.state_changed' BEGIN SELECT RAISE(ABORT,'disk'); END"
        )
    with pytest.raises(sqlite3.IntegrityError):
        journal.prepare(OwnedLaunch("owned", "run", "runtime", "worker", str(tmp_path)))
    assert not journal.pending()


def test_foreign_runtime_cannot_create_an_owned_launch(tmp_path: Path) -> None:
    case = run_case(tmp_path / "run.sqlite")
    journal = SqliteProcessJournal(case.database, 4096)
    with pytest.raises(ValueError, match="admitted runtime"):
        journal.prepare(OwnedLaunch("owned", "run", "foreign", "worker", str(tmp_path)))
    assert not journal.pending()
