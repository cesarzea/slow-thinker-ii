"""Native usage partitions settle once, including reasoning output."""

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object
from support.native_model import response

from models.fixtures import payload, policy, result


def test_exact_categories_and_reasoning_output_settle_once() -> None:
    evidence = policy().reconcile(result(payload()))
    assert evidence.amount == 6024 and evidence.usage_json is not None
    usage = json_object(decode_json(evidence.usage_json))
    assert (
        usage["status"] == "verified"
        and usage["billing_assumptions"] == "reviewed_direct_schedule_and_calendar"
    )
    assert json_object(usage["reported_usage"])["completion_tokens_details"] == {
        "reasoning_tokens": 2
    }


@pytest.mark.parametrize(
    "field,value,reason",
    [
        ("prompt_tokens", -1, "incomplete_usage"),
        ("completion_tokens", True, "incomplete_usage"),
        ("prompt_cache_hit_tokens", None, "incomplete_usage"),
        ("prompt_cache_miss_tokens", 7, "inconsistent_usage"),
        ("total_tokens", 16, "inconsistent_usage"),
        ("prompt_tokens", 13, "inconsistent_usage"),
    ],
)
def test_bad_usage_retains_exposure(field: str, value: JsonValue, reason: str) -> None:
    value_record = payload()
    body = json_object(value_record["response"])
    usage = json_object(body["usage"])
    usage[field] = value
    body["usage"] = usage
    value_record["response"] = body
    evidence = policy().reconcile(result(value_record))
    assert evidence.amount is None and evidence.usage_json is not None
    assert json_object(decode_json(evidence.usage_json))["reason"] == reason


@pytest.mark.parametrize(
    "fault", ["model", "usage", "response", "error", "provider_failure", "capacity"]
)
def test_unproven_or_excessive_outcomes_are_unresolved(fault: str) -> None:
    value: JsonObject = payload()
    body = json_object(value["response"])
    if fault == "model":
        body["model"] = "other"
    elif fault == "usage":
        body["usage"] = []
    elif fault == "capacity":
        body["usage"] = {
            "prompt_tokens": 1_000_001,
            "prompt_cache_hit_tokens": 0,
            "prompt_cache_miss_tokens": 1_000_001,
            "completion_tokens": 3,
            "total_tokens": 1_000_004,
        }
    elif fault in {"response", "provider_failure"}:
        value = {"error": {"origin": "provider", "status": 429}}
    if "response" in value:
        value["response"] = body
    evidence = policy().reconcile(result(value, error=fault in {"error", "provider_failure"}))
    assert evidence.amount is None


def test_legacy_openai_usage_amount_is_unchanged() -> None:
    evidence = policy("openai").reconcile(result({"response": response()}))
    assert evidence.amount == 2390 and evidence.source == "openai.usage"
