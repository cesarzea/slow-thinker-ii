"""Import only the reviewed direct DeepSeek Flash table and retain its normalized source."""

import re
from fractions import Fraction
from hashlib import sha256

from slow_thinker_ii.accounting import Tariff, TariffRevision, TokenRates
from slow_thinker_ii.contracts import JsonObject, encode_json

from ._deepseek_calendar import schedule_policy
from ._html_table import PricingTable, text

DEEPSEEK_SOURCE_URL = "https://api-docs.deepseek.com/quick_start/pricing/"
DEEPSEEK_PROFILE_ID = "deepseek.flash.direct.v1"
MAX_PRICING_BYTES = 256 * 1024
CATEGORIES = {
    "1M INPUT TOKENS (CACHE MISS)": "input",
    "1M INPUT TOKENS (CACHE HIT)": "cached",
    "1M OUTPUT TOKENS": "output",
}


def parse_deepseek_pricing(payload: bytes, now: int) -> TariffRevision:
    if len(payload) > MAX_PRICING_BYTES or type(now) is not int or now < 0:
        raise ValueError("Invalid pricing capture size or timestamp")
    captured = payload.decode("utf-8", errors="strict")
    parser = PricingTable()
    parser.feed(captured)
    parser.close()
    rows = parser.grid()
    column = model_column(rows)
    validate_schedule(text(" ".join(parser.text)))
    peak, off_peak = price_bands(rows, column)
    normalized: JsonObject = {
        "profile": DEEPSEEK_PROFILE_ID,
        "model": "deepseek-flash",
        "currency": "USD",
        "input_capacity": 1_000_000,
        "output_capacity": 384_000,
        "peak": rate_record(peak),
        "off_peak": rate_record(off_peak),
        "schedule": schedule_policy(),
        "cache_creation": "no_separate_surcharge",
    }
    source = encode_json({"captured_html": captured, "normalized": normalized})
    tariff = Tariff(
        DEEPSEEK_PROFILE_ID, "deepseek-flash", 1_000_000, 384_000, 1_000_001, peak, peak
    )
    return TariffRevision(
        sha256(source.encode()).hexdigest(), now, DEEPSEEK_SOURCE_URL, tariff, source
    )


def model_column(rows: list[list[str]]) -> int:
    headers = [row for row in rows if row[0] == "MODEL"]
    if len(headers) != 1 or headers[0].count("deepseek-flash") != 1:
        raise ValueError("Pricing requires exactly one DeepSeek Flash model")
    column = headers[0].index("deepseek-flash")
    required = {
        "BASE URL (OpenAI Format)": "https://api.deepseek.com",
        "CONTEXT LENGTH": "1M",
        "MAX OUTPUT": "MAXIMUM: 384K",
    }
    for name, expected in required.items():
        matches = [row[column] for row in rows if row[0] == name]
        if matches != [expected]:
            raise ValueError("Reviewed provider identity or capacity changed")
    return column


def validate_schedule(value: str) -> None:
    required = (
        "Off-peak rates are half of the peak rates.",
        "Peak hours are 01:00 - 04:00 and 06:00 - 10:00 UTC, Monday through Friday, "
        "excluding Chinese public holidays.",
        "All other hours are off-peak, including weekends and Chinese public holidays in full.",
    )
    if any(part not in value for part in required):
        raise ValueError("Unsupported direct billing schedule")


def price_bands(rows: list[list[str]], column: int) -> tuple[TokenRates, TokenRates]:
    rates: dict[tuple[str, str], Fraction] = {}
    for row in rows:
        if row[0] != "PRICING":
            continue
        category = CATEGORIES.get(row[1])
        key = row[2], str(category)
        if category is None or row[2] not in ("PEAK", "OFF-PEAK") or key in rates:
            raise ValueError("Unsupported or duplicate billing category")
        if not re.fullmatch(r"\$(?:0|[1-9]\d{0,2})(?:\.\d{1,18})?", row[column]):
            raise ValueError("USD token rates are required")
        rates[key] = Fraction(row[column][1:]) / 1_000_000
    if len(rates) != 6 or any(
        rates[("OFF-PEAK", name)] * 2 != rates[("PEAK", name)] for name in CATEGORIES.values()
    ):
        raise ValueError("Missing or inconsistent direct token rates")
    return band(rates, "PEAK"), band(rates, "OFF-PEAK")


def band(rates: dict[tuple[str, str], Fraction], period: str) -> TokenRates:
    return TokenRates(
        rates[(period, "input")],
        rates[(period, "cached")],
        rates[(period, "input")],
        rates[(period, "output")],
    )


def rate_record(rates: TokenRates) -> JsonObject:
    return {
        "input": str(rates.input),
        "cached": str(rates.cached),
        "cache_write": str(rates.cache_write),
        "output": str(rates.output),
    }
