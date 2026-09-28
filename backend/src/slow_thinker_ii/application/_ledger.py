"""Coordinate accounting rules within one storage transaction."""

from contextlib import AbstractContextManager
from typing import Protocol

from slow_thinker_ii.accounting import (
    BudgetScope,
    Reservation,
    ScopeKeys,
    SettlementOutcome,
    admit,
)


class LedgerTransaction(Protocol):
    def scopes(self, keys: ScopeKeys) -> tuple[BudgetScope, BudgetScope, BudgetScope]: ...
    def reserve(self, request: Reservation) -> None: ...
    def dispatched(self, attempt_id: str) -> None: ...
    def settle(self, attempt_id: str, amount: int, source: str) -> SettlementOutcome: ...
    def release_unsent(self, attempt_id: str) -> None: ...


class LedgerStore(Protocol):
    def begin(self) -> AbstractContextManager[LedgerTransaction]: ...


class BudgetLedger:
    def __init__(self, store: LedgerStore) -> None:
        self._store = store

    def reserve(self, request: Reservation) -> None:
        with self._store.begin() as transaction:
            admit(transaction.scopes(request.scopes), request.bound)
            transaction.reserve(request)

    def dispatched(self, attempt_id: str) -> None:
        with self._store.begin() as transaction:
            transaction.dispatched(attempt_id)

    def settle(self, attempt_id: str, amount: int, source: str) -> SettlementOutcome:
        with self._store.begin() as transaction:
            return transaction.settle(attempt_id, amount, source)

    def release_unsent(self, attempt_id: str) -> None:
        with self._store.begin() as transaction:
            transaction.release_unsent(attempt_id)
