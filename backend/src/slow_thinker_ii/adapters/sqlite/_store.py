"""Expose typed ledger operations without exposing SQLite to the application."""

from collections.abc import Generator
from contextlib import contextmanager

from slow_thinker_ii.accounting import BudgetScope
from slow_thinker_ii.application import LedgerTransaction

from ._database import SqliteDatabase
from ._ledger import SqliteLedgerTransaction


class SqliteLedgerStore:
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def create_scope(self, scope: BudgetScope) -> None:
        with self._database.transaction() as connection:
            connection.execute(
                "INSERT INTO budget_scopes(kind,scope_id,cap,settled,reserved) VALUES (?,?,?,?,?)",
                (scope.kind, scope.key, scope.cap, scope.settled, scope.outstanding),
            )

    @contextmanager
    def begin(self) -> Generator[LedgerTransaction]:
        with self._database.transaction() as connection:
            yield SqliteLedgerTransaction(connection)
