"""Existing ledger data survives verified backups and interrupted schema upgrades."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, _migrations

ROOT = Path(__file__).resolve().parents[3]


def legacy(path: Path) -> None:
    schema = ROOT / "backend/src/slow_thinker_ii/adapters/sqlite/schema.sql"
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.executescript(schema.read_text())
        connection.execute("PRAGMA user_version=1")
        connection.execute("INSERT INTO budget_scopes VALUES('month','2026-09',1000,37,100)")


def test_migration_preserves_money_and_retains_a_verified_old_schema(tmp_path: Path) -> None:
    path = tmp_path / "legacy.sqlite"
    legacy(path)
    database = SqliteDatabase(path)
    database.initialize()
    database.initialize()
    backups = list(tmp_path.glob("*.backup"))
    assert len(backups) == 1
    with closing(sqlite3.connect(backups[0])) as backup:
        assert backup.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert backup.execute("PRAGMA user_version").fetchone()[0] == 1
        assert backup.execute("SELECT settled,reserved FROM budget_scopes").fetchone() == (37, 100)
    with database.transaction() as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 5
        assert tuple(
            connection.execute("SELECT settled,reserved FROM budget_scopes").fetchone()
        ) == (37, 100)
        assert connection.execute("SELECT COUNT(*) FROM managed_runs").fetchone()[0] == 0


def test_failed_migration_rolls_back_schema_and_keeps_original_money(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "legacy.sqlite"
    legacy(path)
    execute = _migrations.execute_schema

    def fail(connection: sqlite3.Connection, source: str) -> None:
        execute(connection, source)
        raise sqlite3.OperationalError("injected migration failure")

    monkeypatch.setattr(_migrations, "execute_schema", fail)
    with pytest.raises(sqlite3.OperationalError):
        SqliteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("SELECT settled,reserved FROM budget_scopes").fetchone() == (
            37,
            100,
        )
        assert (
            connection.execute(
                "SELECT name FROM sqlite_master WHERE name='managed_runs'"
            ).fetchone()
            is None
        )
    assert len(list(tmp_path.glob("*.backup"))) == 1


def test_concurrent_write_duringbackup_aborts_migration(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    path = tmp_path / "legacy.sqlite"
    legacy(path)
    backup = _migrations.backup

    def concurrent_write(connection: sqlite3.Connection, target: Path) -> None:
        backup(connection, target)
        with closing(sqlite3.connect(target)) as writer, writer:
            writer.execute("UPDATE budget_scopes SET settled=38")

    monkeypatch.setattr(_migrations, "backup", concurrent_write)
    with pytest.raises(RuntimeError, match="changed during migration"):
        SqliteDatabase(path).initialize()
    with closing(sqlite3.connect(path)) as connection:
        assert connection.execute("PRAGMA user_version").fetchone()[0] == 1
        assert connection.execute("SELECT settled FROM budget_scopes").fetchone()[0] == 38
