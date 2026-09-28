"""Native usage settles disjoint input categories once, using the saved billing revision."""

import pytest
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.contracts import JsonValue, OperationResult, encode_json, json_object
from support.native_model import profile, response


def test_quote_and_exact_settlement_use_the_same_tariff() -> None:
    policy = OpenAIPricePolicy(profile())
    arguments = '{"request":{"model":"bound-model","messages":[{"role":"user","content":"x"}]}}'
    quote = policy.quote(arguments)
    assert quote.bound == 262_506_000 and quote.tariff_revision == profile().revision.digest
    evidence = policy.reconcile(OperationResult(encode_json({"response": response()}), False))
    assert evidence.amount == 2390 and evidence.source == "openai.usage"


@pytest.mark.parametrize(
    "field,value", [("usage", None), ("model", "unreviewed"), ("service_tier", "flex")]
)
def test_missing_usage_or_wrong_billing_identity_keeps_cost_unknown(
    field: str, value: JsonValue
) -> None:
    body = response()
    body[field] = value
    evidence = OpenAIPricePolicy(profile()).reconcile(
        OperationResult(encode_json({"response": body}), False)
    )
    assert evidence.amount is None and evidence.usage_json is not None


@pytest.mark.parametrize("fault", ["missing", "overlap", "negative", "boolean", "total"])
def test_incomplete_or_inconsistent_categories_never_release_a_reservation(fault: str) -> None:
    body = response()
    usage = json_object(body["usage"])
    details = json_object(usage["prompt_tokens_details"])
    if fault == "missing":
        del details["cache_write_tokens"]
    elif fault == "overlap":
        details["cache_write_tokens"] = 12
    elif fault == "negative":
        usage["completion_tokens"] = -1
    elif fault == "boolean":
        usage["prompt_tokens"] = True
    else:
        usage["total_tokens"] = 1
    usage["prompt_tokens_details"] = details
    body["usage"] = usage
    evidence = OpenAIPricePolicy(profile()).reconcile(
        OperationResult(encode_json({"response": body}), False)
    )
    assert evidence.amount is None
    assert evidence.usage_json is not None and '"unavailable"' in evidence.usage_json
