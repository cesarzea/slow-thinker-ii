"""Reviewed tariff documents: USD per million tokens, converted exactly to rates per token."""

import re
from fractions import Fraction
from itertools import combinations

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._rates import Rates, Tariff, Window

TOKENS_PER_PRICED_UNIT = 1_000_000
MINUTES_PER_DAY = 1440
_DECIMAL = re.compile(r"[0-9]{1,9}(?:\.[0-9]{1,18})?")
_TIME = re.compile(r"(?:[01][0-9]|2[0-3]):[0-5][0-9]")
_NONE: frozenset[str] = frozenset()
_TARIFF = frozenset({"reviewed_on", "source", "rates"})
_TARIFF_OPTIONAL = frozenset({"long_context", "windows"})
_RATES = frozenset({"input", "output"})
_RATES_OPTIONAL = frozenset({"cached_input", "cache_write"})
_LONG_CONTEXT = frozenset({"above_input_tokens", "rates"})
_WINDOW = frozenset({"weekdays", "start", "end", "rates"})


def parse_tariff(
    document: JsonValue, *, byte_bounded_input: bool = True, input_capacity: int | None = None
) -> Tariff:
    fields = _fields(document, "tariff", _TARIFF, _TARIFF_OPTIONAL)
    if not byte_bounded_input and input_capacity is None:
        raise ValueError("A tariff without byte-bounded input requires an input capacity")
    if input_capacity is not None and input_capacity < 1:
        raise ValueError("The input capacity must be a positive number of tokens")
    threshold, long_context = _long_context(fields)
    return Tariff(
        reviewed_on=_text(fields["reviewed_on"], "tariff.reviewed_on"),
        source=_text(fields["source"], "tariff.source"),
        rates=_rates(fields["rates"], "tariff.rates"),
        long_context_above=threshold,
        long_context=long_context,
        windows=_windows(fields),
        byte_bounded_input=byte_bounded_input,
        input_capacity=input_capacity,
    )


def _fields(
    value: JsonValue, name: str, required: frozenset[str], optional: frozenset[str] = _NONE
) -> JsonObject:
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    unknown = sorted(set(value) - required - optional)
    if unknown:
        raise ValueError(f"{name} has unknown fields: {', '.join(unknown)}")
    missing = sorted(required - set(value))
    if missing:
        raise ValueError(f"{name} is missing fields: {', '.join(missing)}")
    return value


def _text(value: JsonValue, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{name} must be a non-empty string")
    return value


def _rates(value: JsonValue, name: str) -> Rates:
    fields = _fields(value, name, _RATES, _RATES_OPTIONAL)
    return Rates(
        input=_rate(fields["input"], f"{name}.input"),
        cached_input=_optional_rate(fields, "cached_input", name),
        cache_write=_optional_rate(fields, "cache_write", name),
        output=_rate(fields["output"], f"{name}.output"),
    )


def _optional_rate(fields: JsonObject, key: str, name: str) -> Fraction | None:
    return _rate(fields[key], f"{name}.{key}") if key in fields else None


def _rate(value: JsonValue, name: str) -> Fraction:
    if not isinstance(value, str) or _DECIMAL.fullmatch(value) is None:
        raise ValueError(f"{name} must be a non-negative decimal string")
    return Fraction(value) / TOKENS_PER_PRICED_UNIT


def _long_context(fields: JsonObject) -> tuple[int | None, Rates | None]:
    if "long_context" not in fields:
        return None, None
    context = _fields(fields["long_context"], "tariff.long_context", _LONG_CONTEXT)
    threshold = context["above_input_tokens"]
    if not isinstance(threshold, int) or isinstance(threshold, bool) or threshold < 0:
        raise ValueError("tariff.long_context.above_input_tokens must be a non-negative integer")
    return threshold, _rates(context["rates"], "tariff.long_context.rates")


def _windows(fields: JsonObject) -> tuple[Window, ...]:
    items = fields.get("windows", [])
    if not isinstance(items, list):
        raise ValueError("tariff.windows must be a list")
    windows = tuple(_window(item, f"tariff.windows[{index}]") for index, item in enumerate(items))
    if any(_overlap(first, second) for first, second in combinations(windows, 2)):
        raise ValueError("tariff.windows must not overlap")
    return windows


def _overlap(first: Window, second: Window) -> bool:
    if not first.weekdays & second.weekdays:
        return False
    return first.start_minute < second.end_minute and second.start_minute < first.end_minute


def _window(value: JsonValue, name: str) -> Window:
    fields = _fields(value, name, _WINDOW)
    start = _minute(fields["start"], f"{name}.start")
    end = _minute(fields["end"], f"{name}.end")
    if end <= start:
        raise ValueError(f"{name} must end after it starts")
    weekdays = _weekdays(fields["weekdays"], f"{name}.weekdays")
    return Window(weekdays, start, end, _rates(fields["rates"], f"{name}.rates"))


def _weekdays(value: JsonValue, name: str) -> frozenset[int]:
    items = value if isinstance(value, list) else []
    days = [day for day in items if isinstance(day, int) and not isinstance(day, bool)]
    valid = [day for day in days if 1 <= day <= 7]
    if not items or len(valid) != len(items) or len(set(valid)) != len(valid):
        raise ValueError(f"{name} must list distinct ISO weekdays from 1 to 7")
    return frozenset(valid)


def _minute(value: JsonValue, name: str) -> int:
    if value == "24:00":
        return MINUTES_PER_DAY
    if not isinstance(value, str) or _TIME.fullmatch(value) is None:
        raise ValueError(f"{name} must be a UTC time from 00:00 to 24:00")
    return int(value[:2]) * 60 + int(value[3:])
