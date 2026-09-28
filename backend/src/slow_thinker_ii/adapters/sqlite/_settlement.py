"""Record late usage once, preserving conflicting evidence and full excess costs."""

import sqlite3

from slow_thinker_ii.accounting import MAX_QUANTA, ScopeKeys, SettlementOutcome

from ._rows import attempt, integer, scope_keys, text


def evidence(
    connection: sqlite3.Connection, key: str, event: str, amount: int, source: str
) -> None:
    connection.execute(
        "INSERT INTO spending_evidence(attempt_id,event,amount,source) VALUES (?,?,?,?)",
        (key, event, amount, source),
    )


def adjust(connection: sqlite3.Connection, row: sqlite3.Row, amount: int) -> None:
    keys = ScopeKeys(text(row, "run_id"), text(row, "session_id"), text(row, "month_id"))
    for kind, key in scope_keys(keys):
        connection.execute(
            "UPDATE budget_scopes SET reserved=reserved-?, settled=settled+? "
            "WHERE kind=? AND scope_id=?",
            (integer(row, "bound"), amount, kind, key),
        )


def settle(connection: sqlite3.Connection, key: str, amount: int, source: str) -> SettlementOutcome:
    if not source or amount < 0 or amount > MAX_QUANTA:
        raise ValueError("Invalid settlement evidence")
    row = attempt(connection, key)
    if text(row, "state") == "settled":
        if integer(row, "amount") == amount and text(row, "source") == source:
            return "duplicate"
        evidence(connection, key, "settlement_conflict", amount, source)
        return "conflict"
    if text(row, "state") != "dispatched":
        raise ValueError("Only a possibly dispatched attempt can be settled")
    adjust(connection, row, amount)
    connection.execute(
        "UPDATE spending_attempts SET state='settled',amount=?,source=? WHERE attempt_id=?",
        (amount, source, key),
    )
    evidence(connection, key, "settled", amount, source)
    return "applied"
