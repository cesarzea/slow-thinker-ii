"""Immutable exact token rates for the reviewed text billing profile."""

from dataclasses import dataclass
from fractions import Fraction

from ._money import MAX_QUANTA, QUANTA_PER_USD


@dataclass(frozen=True)
class TokenRates:
    input: Fraction
    cached: Fraction
    cache_write: Fraction
    output: Fraction

    def __post_init__(self) -> None:
        if min(self.input, self.cached, self.cache_write, self.output) < 0:
            raise ValueError("Negative token rate")


@dataclass(frozen=True)
class TokenUsage:
    prompt: int
    cached: int
    cache_write: int
    completion: int

    def __post_init__(self) -> None:
        if min(self.prompt, self.cached, self.cache_write, self.completion) < 0:
            raise ValueError("Negative token count")
        if self.cached + self.cache_write > self.prompt:
            raise ValueError("Cache categories exceed total input")


@dataclass(frozen=True)
class Tariff:
    profile: str
    model: str
    input_capacity: int
    output_capacity: int
    long_context_start: int
    short: TokenRates
    long: TokenRates

    def reservation(self, output_limit: int) -> int:
        if output_limit < 1 or output_limit > self.output_capacity:
            raise ValueError("Unsupported output limit")
        rates = (self.short, self.long)
        input_rate = max(max(rate.input, rate.cached, rate.cache_write) for rate in rates)
        output_rate = max(rate.output for rate in rates)
        return account_fraction(self.input_capacity * input_rate + output_limit * output_rate)

    def charge(self, usage: TokenUsage) -> Fraction:
        if usage.prompt > self.input_capacity or usage.completion > self.output_capacity:
            raise ValueError("Usage exceeds reviewed model capacity")
        rates = self.long if usage.prompt >= self.long_context_start else self.short
        return (
            (usage.prompt - usage.cached - usage.cache_write) * rates.input
            + usage.cached * rates.cached
            + usage.cache_write * rates.cache_write
            + usage.completion * rates.output
        )


def account_fraction(amount: Fraction) -> int:
    scaled = amount * QUANTA_PER_USD
    accounted = -(-scaled.numerator // scaled.denominator)
    if amount < 0 or accounted > MAX_QUANTA:
        raise ValueError("Charge exceeds ledger range")
    return accounted


@dataclass(frozen=True)
class TariffRevision:
    digest: str
    retrieved_at: int
    source: str
    tariff: Tariff
    source_json: str


@dataclass(frozen=True)
class RefreshStatus:
    last_attempt: int | None
    last_success: int | None
    revision: str | None
    error: str | None
