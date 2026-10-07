"""Budget scopes and the UTC keys of the day and month scopes."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from ._charges import utc


@dataclass(frozen=True)
class Scope:
    kind: Literal["run", "day", "month"]
    key: str
    limit: int
    used: int


def first_exhausted(scopes: Sequence[Scope], amount: int) -> Scope | None:
    return next((scope for scope in scopes if scope.used + amount > scope.limit), None)


def day_key(at: datetime) -> str:
    moment = utc(at)
    return f"{moment.year:04d}-{moment.month:02d}-{moment.day:02d}"


def month_key(at: datetime) -> str:
    moment = utc(at)
    return f"{moment.year:04d}-{moment.month:02d}"
