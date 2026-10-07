"""Every malformed tariff document is rejected with a message naming the offending field."""

import pytest
from slow_thinker_ii.accounting import parse_tariff
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .step_one import FLASH, LUNA, changed, removed, step_one_tariff

RATE = "must be a non-negative decimal string"
WEEKDAYS = "tariff.windows[0].weekdays must list distinct ISO weekdays from 1 to 7"
TIME = "must be a UTC time from 00:00 to 24:00"
THRESHOLD = "tariff.long_context.above_input_tokens must be a non-negative integer"


def luna(path: tuple[str | int, ...], value: JsonValue) -> JsonObject:
    return changed(step_one_tariff(LUNA), path, value)


def flash(path: tuple[str | int, ...], value: JsonValue) -> JsonObject:
    return changed(step_one_tariff(FLASH), path, value)


def window(field: str, value: JsonValue) -> JsonObject:
    return flash(("windows", 0, field), value)


ERRORS: list[tuple[JsonValue, str]] = [
    ([], "tariff must be an object"),
    (luna(("currency",), "USD"), "tariff has unknown fields: currency"),
    (
        changed(luna(("currency",), "USD"), ("batch",), 1),
        "tariff has unknown fields: batch, currency",
    ),
    (removed(step_one_tariff(LUNA), "source", "rates"), "tariff is missing fields: rates, source"),
    (luna(("reviewed_on",), ""), "tariff.reviewed_on must be a non-empty string"),
    (luna(("source",), 7), "tariff.source must be a non-empty string"),
    (luna(("rates",), "0.1"), "tariff.rates must be an object"),
    (luna(("rates", "batch"), "1"), "tariff.rates has unknown fields: batch"),
    (flash(("rates",), {"input": "1"}), "tariff.rates is missing fields: output"),
    (luna(("rates", "input"), "-0.10"), f"tariff.rates.input {RATE}"),
    (luna(("rates", "output"), 0.5), f"tariff.rates.output {RATE}"),
    (luna(("rates", "input"), "1e-3"), f"tariff.rates.input {RATE}"),
    (luna(("rates", "cached_input"), "x"), f"tariff.rates.cached_input {RATE}"),
    (luna(("rates", "cache_write"), ".5"), f"tariff.rates.cache_write {RATE}"),
    (luna(("long_context",), []), "tariff.long_context must be an object"),
    (luna(("long_context", "above_input_tokens"), -1), THRESHOLD),
    (luna(("long_context", "above_input_tokens"), True), THRESHOLD),
    (luna(("long_context", "above_input_tokens"), "1"), THRESHOLD),
    (luna(("long_context", "rates", "output"), "x"), f"tariff.long_context.rates.output {RATE}"),
    (flash(("windows",), {}), "tariff.windows must be a list"),
    (flash(("windows", 0), "01:00"), "tariff.windows[0] must be an object"),
    (window("label", "peak"), "tariff.windows[0] has unknown fields: label"),
    (window("weekdays", []), WEEKDAYS),
    (window("weekdays", [0]), WEEKDAYS),
    (window("weekdays", [8]), WEEKDAYS),
    (window("weekdays", [1, 1]), WEEKDAYS),
    (window("weekdays", ["1"]), WEEKDAYS),
    (window("weekdays", [True]), WEEKDAYS),
    (window("weekdays", 1), WEEKDAYS),
    (window("start", "1:00"), f"tariff.windows[0].start {TIME}"),
    (window("start", "24:01"), f"tariff.windows[0].start {TIME}"),
    (window("start", "01:60"), f"tariff.windows[0].start {TIME}"),
    (window("start", 60), f"tariff.windows[0].start {TIME}"),
    (window("end", "25:00"), f"tariff.windows[0].end {TIME}"),
    (window("end", "01:00"), "tariff.windows[0] must end after it starts"),
    (window("start", "24:00"), "tariff.windows[0] must end after it starts"),
    (window("rates", {"input": "1", "output": "-1"}), f"tariff.windows[0].rates.output {RATE}"),
    (window("end", "06:01"), "tariff.windows must not overlap"),
    (flash(("windows", 1, "start"), "03:59"), "tariff.windows must not overlap"),
]


@pytest.mark.parametrize(("document", "message"), ERRORS)
def test_malformed_tariffs_are_rejected(document: JsonValue, message: str) -> None:
    with pytest.raises(ValueError) as raised:
        parse_tariff(document)
    assert str(raised.value) == message
