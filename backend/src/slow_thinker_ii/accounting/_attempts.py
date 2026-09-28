"""Immutable spending identities, independent of persistence and execution."""

from dataclasses import dataclass
from typing import Literal

from ._money import MAX_QUANTA


@dataclass(frozen=True)
class ScopeKeys:
    run: str
    session: str
    month: str

    def __post_init__(self) -> None:
        if not all((self.run, self.session, self.month)):
            raise ValueError("All spending scope identities are required")


@dataclass(frozen=True)
class Reservation:
    attempt_id: str
    scopes: ScopeKeys
    bound: int

    def __post_init__(self) -> None:
        if not self.attempt_id or self.bound < 0 or self.bound > MAX_QUANTA:
            raise ValueError("Invalid spending reservation")


type SettlementOutcome = Literal["applied", "duplicate", "conflict"]
