"""Schema upgrades refuse unfinished v2 runs until explicit recovery has closed them."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteRunStore
from slow_thinker_ii.application import recover_runs

ROOT = Path(__file__).resolve().parents[3]


def version_two(path: Path) -> None:
    schemas = ROOT / "backend/src/slow_thinker_ii/adapters/sqlite"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.executescript((schemas / "schema.sql").read_text())
        connection.executescript((schemas / "execution.sql").read_text())
        connection.execute("PRAGMA user_version=2")
        connection.execute(
            "INSERT INTO managed_runs(run_id,graph_revision,session_id,month_id,runtime_id,"
            "deadline,snapshot_json,state) VALUES("
            "'run','revision','session','2026-09','old',100,'{}','running')"
        )


def test_v2_runs_must_be_recovered_before_receipt_schema_migration(tmp_path: Path) -> None:
    path = tmp_path / "old.sqlite"
    version_two(path)
    database = SqliteDatabase(path)
    with pytest.raises(ValueError, match="recovered or terminal"):
        database.initialize()
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 2
        assert connection.execute("SELECT state FROM managed_runs").fetchone()[0] == "running"
    assert recover_runs(SqliteRunStore(database, 4096)) == ("run",)
    database.initialize()
    with database.transaction() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 4
        assert connection.execute("SELECT state FROM managed_runs").fetchone()[0] == "interrupted"
        assert connection.execute("SELECT COUNT(*) FROM call_receipts").fetchone()[0] == 0
    assert list(tmp_path.glob("old.sqlite.v2.*.backup"))
