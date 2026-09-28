"""Decide admission; the persistence boundary applies all scopes atomically."""

from dataclasses import dataclass
from typing import Literal

from ._money import MAX_QUANTA

type ScopeKind = Literal["run", "session", "month"]


@dataclass(frozen=True)
class BudgetScope:
    kind: ScopeKind
    key: str
    cap: int
    settled: int
    outstanding: int

    def __post_init__(self) -> None:
        if not self.key:
            raise ValueError("A scope requires a key")
        for amount in (self.cap, self.settled, self.outstanding):
            if amount < 0 or amount > MAX_QUANTA:
                raise ValueError("Invalid scope amount")


class BudgetExceeded(ValueError):
    """An admission was refused without changing any scope."""

    def __init__(self, scope: BudgetScope, reservation: int) -> None:
        self.scope = scope
        self.reservation = reservation
        super().__init__(f"Insufficient {scope.kind} budget")


def admit(scopes: tuple[BudgetScope, BudgetScope, BudgetScope], reservation: int) -> None:
    if {scope.kind for scope in scopes} != {"run", "session", "month"}:
        raise ValueError("Admission requires run, session and month scopes")
    if reservation < 0 or reservation > MAX_QUANTA:
        raise ValueError("Invalid reservation")
    for scope in scopes:
        if scope.settled + scope.outstanding + reservation > scope.cap:
            raise BudgetExceeded(scope, reservation)
