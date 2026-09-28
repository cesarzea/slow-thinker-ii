"""Validate stored ledger fields before rebuilding domain values."""

import sqlite3

from slow_thinker_ii.accounting import BudgetScope, ScopeKeys, ScopeKind


def integer(row: sqlite3.Row, key: str) -> int:
    value: object = row[key]
    if type(value) is not int:
        raise ValueError(f"Invalid stored integer: {key}")
    return value


def text(row: sqlite3.Row, key: str) -> str:
    value: object = row[key]
    if not isinstance(value, str):
        raise ValueError(f"Invalid stored text: {key}")
    return value


def scope_keys(keys: ScopeKeys) -> tuple[tuple[ScopeKind, str], ...]:
    return (("run", keys.run), ("session", keys.session), ("month", keys.month))


def scope(connection: sqlite3.Connection, kind: ScopeKind, key: str) -> BudgetScope:
    row = connection.execute(
        "SELECT * FROM budget_scopes WHERE kind=? AND scope_id=?",
        (kind, key),
    ).fetchone()
    if row is None:
        raise ValueError("Unknown budget scope")
    return BudgetScope(
        kind, key, integer(row, "cap"), integer(row, "settled"), integer(row, "reserved")
    )


def attempt(connection: sqlite3.Connection, attempt_id: str) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM spending_attempts WHERE attempt_id=?", (attempt_id,)
    ).fetchone()
    if row is None:
        raise ValueError("Unknown spending attempt")
    return row
