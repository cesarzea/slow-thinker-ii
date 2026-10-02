"""Schema v5 is additive and retains interrupted work, sessions, payloads and original budgets."""

import sqlite3
from contextlib import closing
from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from support.sequence_plans import ROOT


def version_four(path: Path) -> None:
    directory = ROOT / "backend/src/slow_thinker_ii/adapters/sqlite"
    with closing(sqlite3.connect(path)) as db, db:
        for name in ("schema.sql", "execution.sql", "receipts.sql", "operator.sql"):
            db.executescript((directory / name).read_text())
        db.execute("PRAGMA user_version=4")
        db.execute("INSERT INTO budget_scopes VALUES('month','2026-09',1000,37,100)")
        db.execute(
            "INSERT INTO managed_runs(run_id,graph_revision,session_id,month_id,"
            "runtime_id,deadline,snapshot_json,state) VALUES "
            "('old','v1','session','2026-09','runtime',100,'{}','running')"
        )


def test_v4_upgrade_preserves_evidence_and_adds_empty_runtime_tables(tmp_path: Path) -> None:
    path = tmp_path / "old.sqlite"
    version_four(path)
    database = SqliteDatabase(path)
    database.initialize()
    database.initialize()
    with database.transaction() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 6
        assert tuple(db.execute("SELECT settled,reserved FROM budget_scopes").fetchone()) == (
            37,
            100,
        )
        assert db.execute("SELECT state FROM managed_runs").fetchone()[0] == "running"
        assert db.execute("SELECT count(*) FROM process_ownership").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM pricing_quarantine").fetchone()[0] == 0
    backups = list(tmp_path.glob("old.sqlite.v4.*.backup"))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
