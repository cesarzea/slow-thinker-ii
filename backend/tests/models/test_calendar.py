"""UTC rate windows respect reviewed Chinese holidays and retain ambiguous exposure."""

import pytest
from slow_thinker_ii.contracts import JsonValue, decode_json, json_object

from models.fixtures import payload, policy, result


@pytest.mark.parametrize(
    "start,amount",
    [
        ("2026-06-22T00:59:00", 3012),
        ("2026-06-22T01:00:00", 6024),
        ("2026-06-22T03:59:00", 6024),
        ("2026-06-22T04:00:00", 3012),
        ("2026-06-22T06:00:00", 6024),
        ("2026-06-22T09:59:00", 6024),
        ("2026-06-22T10:00:00", 3012),
        ("2026-06-20T02:00:00", 3012),
        ("2026-01-02T02:00:00", 3012),
        ("2026-02-17T02:00:00", 3012),
        ("2026-04-06T02:00:00", 3012),
        ("2026-05-04T02:00:00", 3012),
        ("2026-06-19T02:00:00", 3012),
        ("2026-09-25T02:00:00", 3012),
        ("2026-10-01T02:00:00", 3012),
        ("2027-01-02T02:00:00", 3012),
        ("2027-01-04T00:00:00", 3012),
    ],
)
def test_exact_peak_offpeak_calendar_rates(start: str, amount: int) -> None:
    assert policy().reconcile(result(payload(start))).amount == amount


@pytest.mark.parametrize(
    "start,finish",
    [
        ("2026-06-22T00:59:59", "2026-06-22T01:00:00"),
        ("2026-06-22T03:59:59", "2026-06-22T04:00:00"),
        ("2026-06-22T05:59:59", "2026-06-22T06:00:00"),
        ("2026-06-22T09:59:59", "2026-06-22T10:00:00"),
        ("2026-06-22T02:00:00", "2026-06-22T07:00:00"),
        ("2027-01-04T00:00:00", "2027-01-04T11:00:00"),
    ],
)
def test_crossing_actual_or_unreviewed_rate_windows_is_unresolved(start: str, finish: str) -> None:
    evidence = policy().reconcile(result(payload(start, finish)))
    assert evidence.amount is None and evidence.usage_json is not None
    assert json_object(decode_json(evidence.usage_json))["reason"] == "billing_interval_boundary"


def test_masked_holiday_boundary_can_settle_and_future_peak_cannot() -> None:
    value = payload("2026-06-19T00:59:59", "2026-06-19T01:00:01")
    assert policy().reconcile(result(value)).amount == 3012
    evidence = policy().reconcile(result(payload("2027-01-04T02:00:00")))
    assert evidence.amount is None and evidence.usage_json is not None
    assert json_object(decode_json(evidence.usage_json))["reason"] == "unreviewed_billing_interval"


@pytest.mark.parametrize(
    "field,value",
    [
        ("request_started_at", None),
        ("request_started_at", True),
        ("request_started_at", "x"),
        ("response_finished_at", 1),
        ("response_finished_at", 10**100),
    ],
)
def test_missing_regressed_or_impossible_transport_timing_is_unresolved(
    field: str, value: JsonValue
) -> None:
    document = payload()
    timing = json_object(document["transport"])
    timing[field] = value
    document["transport"] = timing
    assert policy().reconcile(result(document)).amount is None


@pytest.mark.parametrize("created", [True, -1, 10**20, "x"])
def test_native_creation_second_must_fit_capture(created: JsonValue) -> None:
    document = payload()
    body = json_object(document["response"])
    body["created"] = created
    document["response"] = body
    evidence = policy().reconcile(result(document))
    assert evidence.amount is None and evidence.usage_json is not None
    assert json_object(decode_json(evidence.usage_json))["reason"] == "inconsistent_provider_timing"


def test_optional_creation_and_whole_second_capture_are_supported() -> None:
    document = payload("2026-06-22T02:00:00.9", "2026-06-22T02:00:01.1")
    assert policy().reconcile(result(document)).amount == 6024
    body = json_object(document["response"])
    body.pop("created")
    document["response"] = body
    assert policy().reconcile(result(document)).amount == 6024
    assert (
        policy().reconcile(result(payload("2026-06-22T02:00:00", "2026-07-22T02:00:00"))).amount
        is None
    )
