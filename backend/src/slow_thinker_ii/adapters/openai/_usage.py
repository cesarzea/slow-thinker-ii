"""Reported categories partition input tokens; absent or inconsistent evidence is not zero."""

from slow_thinker_ii.accounting import TokenUsage
from slow_thinker_ii.contracts import JsonObject, json_object


def token_count(value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("incomplete_usage")
    return value


def reported_usage(response: JsonObject, returned_models: tuple[str, ...]) -> TokenUsage:
    if response.get("model") not in returned_models or response.get("service_tier") != "default":
        raise ValueError("billing_identity_mismatch")
    usage = json_object(response.get("usage"))
    details = json_object(usage.get("prompt_tokens_details"))
    prompt, completion = (
        token_count(usage.get("prompt_tokens")),
        token_count(usage.get("completion_tokens")),
    )
    if "total_tokens" in usage and token_count(usage["total_tokens"]) != prompt + completion:
        raise ValueError("inconsistent_usage")
    return TokenUsage(
        prompt,
        token_count(details.get("cached_tokens")),
        token_count(details.get("cache_write_tokens")),
        completion,
    )
