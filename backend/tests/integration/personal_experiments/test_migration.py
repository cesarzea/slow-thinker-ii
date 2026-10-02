"""Schema v6 preserves old records and its verified v5 backup transactionally."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, _migrations
from support.sequence_plans import ROOT


def version_five(path: Path) -> dict[str, list[tuple[object, ...]]]:
    directory = ROOT / "backend/src/slow_thinker_ii/adapters/sqlite"
    with closing(sqlite3.connect(path)) as db, db:
        for name in ("schema.sql", "execution.sql", "receipts.sql", "operator.sql", "runtime.sql"):
            db.executescript((directory / name).read_text())
        db.execute("PRAGMA user_version=5")
        db.execute("INSERT INTO budget_scopes VALUES('month','2026-09',1000,37,100)")
        db.execute(
            "INSERT INTO managed_runs(run_id,graph_revision,session_id,month_id,runtime_id,"
            "deadline,snapshot_json,state) "
            "VALUES ('old','v1','session','2026-09','runtime',100,'{}','running')"
        )
        db.execute("INSERT INTO operator_sessions VALUES('session','Prior experiment',1)")
        db.execute(
            "INSERT INTO process_ownership(marker,run_id,runtime_id,instance_id,workspace,state) "
            "VALUES('prior','old','runtime','proposer','/fixture','unconfirmed')"
        )
        return saved_tables(db)


def saved_tables(db: sqlite3.Connection) -> dict[str, list[tuple[object, ...]]]:
    tables = db.execute(
        "SELECT name FROM sqlite_master "
        "WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    return {str(row[0]): list(db.execute(f'SELECT * FROM "{row[0]}"').fetchall()) for row in tables}


def test_v5_migration_preserves_every_existing_table_and_verified_backup(tmp_path: Path) -> None:
    path = tmp_path / "previous.sqlite"
    original = version_five(path)
    database = SqliteDatabase(path)
    database.initialize()
    database.initialize()
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 6
        current = saved_tables(db)
        assert {name: current[name] for name in original} == original
        assert current["personal_definitions"] == []
    backups = list(tmp_path.glob("previous.sqlite.v5.*.backup"))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as db:
        assert db.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert db.execute("PRAGMA user_version").fetchone()[0] == 5
        assert saved_tables(db) == original


def test_v5_failed_migration_restores_schema_and_all_prior_rows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "failed.sqlite"
    original = version_five(path)
    execute = _migrations.execute_schema

    def fail(db: sqlite3.Connection, source: str) -> None:
        execute(db, source)
        raise sqlite3.OperationalError("Injected v6 migration failure")

    monkeypatch.setattr(_migrations, "execute_schema", fail)
    with pytest.raises(sqlite3.OperationalError):
        SqliteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 5
        assert saved_tables(db) == original
    assert list(tmp_path.glob("failed.sqlite.v5.*.backup"))


def test_future_schema_is_rejected_without_migration(tmp_path: Path) -> None:
    path = tmp_path / "future.sqlite"
    original = version_five(path)
    with closing(sqlite3.connect(path)) as db, db:
        db.execute("PRAGMA user_version=7")
    with pytest.raises(ValueError, match="Unsupported database schema"):
        SqliteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as db:
        assert db.execute("PRAGMA user_version").fetchone()[0] == 7
        assert saved_tables(db) == original
    assert not list(tmp_path.glob("*.backup"))
