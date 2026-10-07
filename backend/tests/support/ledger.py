"""An in-memory `application.Ledger` following the sqlite adapter's rules."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime

from slow_thinker_ii.accounting import Scope, first_exhausted


@dataclass
class LedgerRow:
    call_id: str
    run_id: str
    day_key: str
    month_key: str
    reserved: int
    charge: int | None  # None while the reservation is open
    estimated: bool


class MemoryLedger:
    """`Ledger` fake: a scope's used amount is the sum of `charge`, or `reserved` while open.

    `reserve` ignores the callers' `Scope.used` and reads the rows, like one transaction.
    """

    def __init__(self) -> None:
        self.rows: dict[str, LedgerRow] = {}

    def reserve(
        self, call_id: str, run_id: str, scopes: Sequence[Scope], amount: int, at: datetime
    ) -> Scope | None:
        current = [Scope(s.kind, s.key, s.limit, self.used(s.kind, s.key)) for s in scopes]
        exhausted = first_exhausted(current, amount)
        if exhausted is None:
            keys = {scope.kind: scope.key for scope in scopes}
            row = LedgerRow(call_id, run_id, keys["day"], keys["month"], amount, None, False)
            self.rows[call_id] = row
        return exhausted

    def settle(self, call_id: str, charge: int, estimated: bool, at: datetime) -> None:
        row = self.rows[call_id]
        row.charge, row.estimated = charge, estimated

    def used(self, kind: str, key: str) -> int:
        return sum(_amount(row) for row in self.rows.values() if _key(row, kind) == key)

    def settle_open(self, run_id: str, at: datetime) -> None:
        for row in self.rows.values():
            if row.run_id == run_id and row.charge is None:
                row.charge, row.estimated = row.reserved, True

    def spent(self, call_id: str, run_id: str, day_key: str, month_key: str, amount: int) -> None:
        """A settled charge of another call, to start a test with prior spending."""
        self.rows[call_id] = LedgerRow(call_id, run_id, day_key, month_key, amount, amount, False)

    def unsettled(self) -> list[str]:
        """Call identifiers whose reservation is still open."""
        return [row.call_id for row in self.rows.values() if row.charge is None]


def _amount(row: LedgerRow) -> int:
    return row.reserved if row.charge is None else row.charge


def _key(row: LedgerRow, kind: str) -> str:
    return {"run": row.run_id, "day": row.day_key, "month": row.month_key}[kind]
