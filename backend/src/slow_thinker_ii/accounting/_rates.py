"""Reviewed tariffs: exact USD rates per token, UTC windows and reported usage."""

from dataclasses import dataclass
from fractions import Fraction


@dataclass(frozen=True)
class Rates:
    input: Fraction
    cached_input: Fraction | None
    cache_write: Fraction | None
    output: Fraction


@dataclass(frozen=True)
class Window:
    weekdays: frozenset[int]
    start_minute: int
    end_minute: int
    rates: Rates


@dataclass(frozen=True)
class Tariff:
    reviewed_on: str
    source: str
    rates: Rates
    long_context_above: int | None
    long_context: Rates | None
    windows: tuple[Window, ...]
    byte_bounded_input: bool
    input_capacity: int | None


@dataclass(frozen=True)
class Usage:
    input: int
    cached_input: int
    cache_write: int
    output: int
