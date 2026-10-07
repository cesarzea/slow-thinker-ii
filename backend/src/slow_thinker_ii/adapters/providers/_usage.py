"""Reported usage as accounting categories; absent or inconsistent evidence is unknown, not zero.

`Usage.input` counts uncached input only: the reported categories partition the prompt.
"""

from slow_thinker_ii.accounting import Usage
from slow_thinker_ii.contracts import JsonObject, JsonValue


def normalized_usage(provider: str, response: JsonObject) -> Usage | None:
    """The usage of a successful response, or `None` when it is missing or inconsistent."""
    usage = response.get("usage")
    if not isinstance(usage, dict):
        return None
    return _openai(usage) if provider == "openai" else _deepseek(usage)


def _openai(usage: JsonObject) -> Usage | None:
    details = usage.get("prompt_tokens_details")
    if not isinstance(details, dict):
        return None
    prompt, output = _count(usage, "prompt_tokens"), _count(usage, "completion_tokens")
    cached, written = _count(details, "cached_tokens"), _count(details, "cache_write_tokens")
    if prompt is None or output is None or cached is None or written is None:
        return None
    if cached + written > prompt or not _total_matches(usage, prompt + output):
        return None
    return Usage(prompt - cached - written, cached, written, output)


def _deepseek(usage: JsonObject) -> Usage | None:
    hit, miss = _count(usage, "prompt_cache_hit_tokens"), _count(usage, "prompt_cache_miss_tokens")
    output = _count(usage, "completion_tokens")
    if hit is None or miss is None or output is None:
        return None
    if "prompt_tokens" in usage and _count(usage, "prompt_tokens") != hit + miss:
        return None
    if not _total_matches(usage, hit + miss + output):
        return None
    return Usage(miss, hit, 0, output)


def _count(document: JsonObject, name: str) -> int | None:
    value: JsonValue = document.get(name)
    return value if type(value) is int and value >= 0 else None


def _total_matches(usage: JsonObject, expected: int) -> bool:
    """A reported `total_tokens` must equal the prompt plus the completion."""
    return "total_tokens" not in usage or _count(usage, "total_tokens") == expected
