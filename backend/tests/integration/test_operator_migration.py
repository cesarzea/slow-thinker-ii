"""Operator tables are additive; upgrading a v3 store preserves runs and monetary evidence."""

import sqlite3
from contextlib import closing
from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteOperatorStore
from support.sequence_plans import ROOT


def test_v3_upgrade_retains_existing_active_run_and_backup(tmp_path: Path) -> None:
    path = tmp_path / "old.sqlite"
    directory = ROOT / "backend/src/slow_thinker_ii/adapters/sqlite"
    with closing(sqlite3.connect(path)) as db, db:
        for name in ("schema.sql", "execution.sql", "receipts.sql"):
            db.executescript((directory / name).read_text())
        db.execute("PRAGMA user_version=3")
        db.execute("INSERT INTO budget_scopes VALUES('month','2026-09',1000,37,100)")
        db.execute(
            "INSERT INTO managed_runs(run_id,graph_revision,session_id,month_id,"
            "runtime_id,deadline,snapshot_json,state) VALUES "
            "('old','v1','session','2026-09','runtime',100,'{}','running')"
        )
    database = SqliteDatabase(path)
    database.initialize()
    database.initialize()
    with database.transaction() as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 4
        assert tuple(db.execute("SELECT settled,reserved FROM budget_scopes").fetchone()) == (
            37,
            100,
        )
        assert db.execute("SELECT state FROM managed_runs").fetchone()[0] == "running"
        assert db.execute("SELECT count(*) FROM operator_commands").fetchone()[0] == 0
    assert SqliteOperatorStore(database, 4096).command("absent") is None
    backups = list(tmp_path.glob("old.sqlite.v3.*.backup"))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 3
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
