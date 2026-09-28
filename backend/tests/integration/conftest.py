"""Isolated durable ledgers for accounting integration cases."""

from dataclasses import dataclass
from pathlib import Path

import pytest
from slow_thinker_ii.accounting import BudgetScope, ScopeKeys, ScopeKind
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteLedgerStore
from slow_thinker_ii.application import BudgetLedger


@dataclass(frozen=True)
class LedgerFixture:
    path: Path
    store: SqliteLedgerStore
    ledger: BudgetLedger
    keys: ScopeKeys


@pytest.fixture
def ledger_case(tmp_path: Path) -> LedgerFixture:
    path = tmp_path / "ledger.sqlite"
    database = SqliteDatabase(path)
    database.initialize()
    store = SqliteLedgerStore(database)
    keys = ScopeKeys("run-1", "session-1", "2026-09")
    scopes: tuple[tuple[ScopeKind, str], ...] = (
        ("run", keys.run),
        ("session", keys.session),
        ("month", keys.month),
    )
    for kind, key in scopes:
        store.create_scope(BudgetScope(kind, key, 1_000, 0, 0))
    return LedgerFixture(path, store, BudgetLedger(store), keys)


def balances(case: LedgerFixture) -> tuple[BudgetScope, BudgetScope, BudgetScope]:
    with case.store.begin() as transaction:
        return transaction.scopes(case.keys)
