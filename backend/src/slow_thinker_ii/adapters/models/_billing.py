"""Validate digest-bound direct billing rates before any quote or reconciliation."""

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256

from slow_thinker_ii.accounting import TariffRevision, TokenRates
from slow_thinker_ii.adapters.tariffs import deepseek_schedule
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object


@dataclass(frozen=True)
class DirectBilling:
    peak: TokenRates
    off_peak: TokenRates
    calendar_year: int
    holidays: tuple[tuple[str, str], ...]


def direct_billing(revision: TariffRevision) -> DirectBilling:
    if sha256(revision.source_json.encode()).hexdigest() != revision.digest:
        raise ValueError("Direct billing source digest mismatch")
    if revision.source != "https://api-docs.deepseek.com/quick_start/pricing/":
        raise ValueError("Unreviewed direct billing source")
    source = json_object(decode_json(revision.source_json))
    normalized = json_object(source["normalized"])
    validate_identity(revision, normalized)
    peak, off_peak = (
        token_rates(json_object(normalized["peak"])),
        token_rates(json_object(normalized["off_peak"])),
    )
    if peak != revision.tariff.short or peak != revision.tariff.long or peak != doubled(off_peak):
        raise ValueError("Direct normalized rates do not match the frozen tariff")
    schedule = json_object(normalized["schedule"])
    calendar = calendar_values(schedule)
    return DirectBilling(peak, off_peak, 2026, holiday_ranges(calendar))


def validate_identity(revision: TariffRevision, value: JsonObject) -> None:
    tariff = revision.tariff
    if (
        value.get("profile"),
        value.get("model"),
        value.get("currency"),
        value.get("input_capacity"),
        value.get("output_capacity"),
        value.get("cache_creation"),
    ) != (
        "deepseek.flash.direct.v1",
        "deepseek-flash",
        "USD",
        tariff.input_capacity,
        tariff.output_capacity,
        "no_separate_surcharge",
    ):
        raise ValueError("Unreviewed direct billing identity")
    if (tariff.input_capacity, tariff.output_capacity, tariff.long_context_start) != (
        1_000_000,
        384_000,
        1_000_001,
    ):
        raise ValueError("Unreviewed direct billing capacity")


def token_rates(value: JsonObject) -> TokenRates:
    if set(value) != {"input", "cached", "cache_write", "output"} or any(
        not isinstance(v, str) for v in value.values()
    ):
        raise ValueError("Invalid normalized token rates")
    try:
        rates = TokenRates(
            *(Fraction(str(value[name])) for name in ("input", "cached", "cache_write", "output"))
        )
    except ZeroDivisionError as error:
        raise ValueError("Invalid normalized token rates") from error
    if rates.cache_write != rates.input:
        raise ValueError("Unsupported separate cache-creation charge")
    return rates


def doubled(value: TokenRates) -> TokenRates:
    return TokenRates(value.input * 2, value.cached * 2, value.cache_write * 2, value.output * 2)


def calendar_values(schedule: JsonObject) -> JsonObject:
    if schedule != deepseek_schedule():
        raise ValueError("Unreviewed direct billing schedule or calendar")
    return json_object(schedule["calendar"])


def holiday_ranges(calendar: JsonObject) -> tuple[tuple[str, str], ...]:
    ranges = calendar["ranges"]
    if not isinstance(ranges, list):
        raise ValueError("Invalid reviewed holiday ranges")
    result: list[tuple[str, str]] = []
    for interval in ranges:
        if not isinstance(interval, list) or len(interval) != 2:
            raise ValueError("Invalid reviewed holiday range")
        start, finish = interval
        if not isinstance(start, str) or not isinstance(finish, str):
            raise ValueError("Invalid reviewed holiday dates")
        result.append((start, finish))
    return tuple(result)
