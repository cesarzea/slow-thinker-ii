"""Implement the ledger transaction port using one SQLite connection."""

import sqlite3

from slow_thinker_ii.accounting import BudgetScope, Reservation, ScopeKeys, SettlementOutcome

from ._rows import attempt, scope, scope_keys, text
from ._settlement import adjust, evidence, settle


class SqliteLedgerTransaction:
    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def scopes(self, keys: ScopeKeys) -> tuple[BudgetScope, BudgetScope, BudgetScope]:
        return (
            scope(self._connection, "run", keys.run),
            scope(self._connection, "session", keys.session),
            scope(self._connection, "month", keys.month),
        )

    def reserve(self, request: Reservation) -> None:
        keys = request.scopes
        self._connection.execute(
            "INSERT INTO spending_attempts(attempt_id,run_id,session_id,month_id,bound,state) "
            "VALUES (?,?,?,?,?,'reserved')",
            (request.attempt_id, keys.run, keys.session, keys.month, request.bound),
        )
        for kind, key in scope_keys(keys):
            self._connection.execute(
                "UPDATE budget_scopes SET reserved=reserved+? WHERE kind=? AND scope_id=?",
                (request.bound, kind, key),
            )
        evidence(self._connection, request.attempt_id, "reserved", request.bound, "platform")

    def dispatched(self, attempt_id: str) -> None:
        row = attempt(self._connection, attempt_id)
        if text(row, "state") != "reserved":
            raise ValueError("An attempt can be dispatched only once")
        self._connection.execute(
            "UPDATE spending_attempts SET state='dispatched' WHERE attempt_id=?",
            (attempt_id,),
        )
        evidence(self._connection, attempt_id, "dispatch_intent", 0, "platform")

    def settle(self, attempt_id: str, amount: int, source: str) -> SettlementOutcome:
        return settle(self._connection, attempt_id, amount, source)

    def release_unsent(self, attempt_id: str) -> None:
        row = attempt(self._connection, attempt_id)
        if text(row, "state") != "reserved":
            raise ValueError("Dispatched or terminal obligations cannot be released as unsent")
        adjust(self._connection, row, 0)
        self._connection.execute(
            "UPDATE spending_attempts SET state='released' WHERE attempt_id=?",
            (attempt_id,),
        )
        evidence(self._connection, attempt_id, "released_unsent", 0, "platform")
