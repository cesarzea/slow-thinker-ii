"""Rates in force, settlement charges and reservation bounds of model calls."""

from datetime import UTC, datetime
from fractions import Fraction

from ._money import account_fraction
from ._rates import Rates, Tariff, Usage

MESSAGE_ALLOWANCE = 16
REQUEST_ALLOWANCE = 64


def utc(at: datetime) -> datetime:
    if at.utcoffset() is None:
        raise ValueError("A time must be timezone-aware")
    return at.astimezone(UTC)


def input_bound(request_bytes: int, messages: int) -> int:
    if request_bytes < 0 or messages < 0:
        raise ValueError("Request sizes must be non-negative")
    return request_bytes + MESSAGE_ALLOWANCE * messages + REQUEST_ALLOWANCE


def rates_at(tariff: Tariff, at: datetime, input_tokens: int) -> Rates:
    threshold = tariff.long_context_above
    if tariff.long_context is not None and threshold is not None and input_tokens > threshold:
        return tariff.long_context
    moment = utc(at)
    minute = moment.hour * 60 + moment.minute
    for window in tariff.windows:
        inside = window.start_minute <= minute < window.end_minute
        if inside and moment.isoweekday() in window.weekdays:
            return window.rates
    return tariff.rates


def charge(tariff: Tariff, usage: Usage, started: datetime, ended: datetime) -> tuple[int, Rates]:
    if min(usage.input, usage.cached_input, usage.cache_write, usage.output) < 0:
        raise ValueError("Token counts must be non-negative")
    reported = usage.input + usage.cached_input + usage.cache_write
    first = rates_at(tariff, started, reported)
    last = rates_at(tariff, ended, reported)
    applied = first if first == last else _higher(first, last)
    amount = (
        usage.input * applied.input
        + usage.cached_input * _billed(applied.cached_input)
        + usage.cache_write * _billed(applied.cache_write)
        + usage.output * applied.output
    )
    return account_fraction(amount), applied


def reservation_bound(tariff: Tariff, input_tokens: int, output_tokens: int) -> int:
    if input_tokens < 0 or output_tokens < 0:
        raise ValueError("Token bounds must be non-negative")
    bound = input_tokens if tariff.byte_bounded_input else tariff.input_capacity
    if bound is None:
        raise ValueError("A tariff without byte-bounded input requires an input capacity")
    rate_sets = _rate_sets(tariff)
    input_rate = max(_highest_input(rates) for rates in rate_sets)
    output_rate = max(rates.output for rates in rate_sets)
    return account_fraction(bound * input_rate + output_tokens * output_rate)


def _rate_sets(tariff: Tariff) -> tuple[Rates, ...]:
    long_context = () if tariff.long_context is None else (tariff.long_context,)
    return (tariff.rates, *long_context, *(window.rates for window in tariff.windows))


def _highest_input(rates: Rates) -> Fraction:
    return max(rates.input, _billed(rates.cached_input), _billed(rates.cache_write))


def _billed(rate: Fraction | None) -> Fraction:
    return Fraction(0) if rate is None else rate


def _higher(first: Rates, last: Rates) -> Rates:
    return Rates(
        input=max(first.input, last.input),
        cached_input=_higher_optional(first.cached_input, last.cached_input),
        cache_write=_higher_optional(first.cache_write, last.cache_write),
        output=max(first.output, last.output),
    )


def _higher_optional(first: Fraction | None, last: Fraction | None) -> Fraction | None:
    present = [rate for rate in (first, last) if rate is not None]
    return max(present) if present else None
