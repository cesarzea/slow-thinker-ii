"""Direct native cache-hit and cache-miss counts partition all reported input usage."""

from slow_thinker_ii.accounting import TokenUsage
from slow_thinker_ii.contracts import JsonObject, json_object


def count(value: object) -> int:
    if type(value) is not int or value < 0:
        raise ValueError("incomplete_usage")
    return value


def direct_usage(response: JsonObject, returned_models: tuple[str, ...]) -> TokenUsage:
    if response.get("model") not in returned_models:
        raise ValueError("billing_identity_mismatch")
    usage = json_object(response.get("usage"))
    prompt, completion = count(usage.get("prompt_tokens")), count(usage.get("completion_tokens"))
    hit, miss = (
        count(usage.get("prompt_cache_hit_tokens")),
        count(usage.get("prompt_cache_miss_tokens")),
    )
    if hit + miss != prompt or count(usage.get("total_tokens")) != prompt + completion:
        raise ValueError("inconsistent_usage")
    return TokenUsage(prompt, hit, 0, completion)
