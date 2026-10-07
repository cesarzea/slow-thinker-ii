"""Reported usage partitions the prompt; missing or inconsistent usage is unknown, never zero."""

import httpx
import pytest
from slow_thinker_ii.accounting import Usage
from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object
from support.examples import FLASH, LUNA

from .fixtures import chat, completion, deepseek_usage, http_provider, model, openai_usage


async def reported(identifier: str, **fields: JsonValue) -> Usage | None:
    """The usage the adapter normalizes from a 200 response carrying `fields`."""
    body = completion(**fields)
    provider, _ = http_provider(lambda request: httpx.Response(200, json=body))
    reply = await provider.complete(model(identifier), chat(identifier), 30)
    assert reply.status == 200 and reply.body == body
    return reply.usage


def without(document: JsonObject, name: str) -> JsonObject:
    return {key: value for key, value in document.items() if key != name}


def openai_details(**changes: JsonValue) -> JsonObject:
    details = json_object(openai_usage()["prompt_tokens_details"])
    return {**openai_usage(), "prompt_tokens_details": {**details, **changes}}


async def test_openai_usage_separates_cached_and_written_input() -> None:
    assert await reported(LUNA, usage=openai_usage()) == Usage(129, 4, 2, 165)
    assert await reported(LUNA, usage=without(openai_usage(), "total_tokens")) == Usage(
        129, 4, 2, 165
    )


async def test_deepseek_usage_separates_cache_hits() -> None:
    assert await reported(FLASH, usage=deepseek_usage()) == Usage(430, 64, 0, 215)
    minimal: JsonObject = {
        "prompt_cache_hit_tokens": 1,
        "prompt_cache_miss_tokens": 2,
        "completion_tokens": 3,
    }
    assert await reported(FLASH, usage=minimal) == Usage(2, 1, 0, 3)


@pytest.mark.parametrize(
    "usage",
    [
        "300 tokens",
        without(openai_usage(), "prompt_tokens_details"),
        {**openai_usage(), "prompt_tokens_details": None},
        without(openai_usage(), "completion_tokens"),
        {**openai_usage(), "prompt_tokens": True},
        {**openai_usage(), "completion_tokens": 1.5},
        {**openai_usage(), "completion_tokens": -1},
        openai_details(cached_tokens=None),
        {**openai_usage(), "prompt_tokens_details": {"cached_tokens": 4}},
        {**openai_usage(), "prompt_tokens": 5, "total_tokens": 170},
        {**openai_usage(), "total_tokens": 301},
        {**openai_usage(), "total_tokens": "300"},
    ],
)
async def test_missing_or_inconsistent_openai_usage_is_unknown(usage: JsonValue) -> None:
    assert await reported(LUNA, usage=usage) is None


@pytest.mark.parametrize(
    "usage",
    [
        without(deepseek_usage(), "prompt_cache_hit_tokens"),
        without(deepseek_usage(), "prompt_cache_miss_tokens"),
        without(deepseek_usage(), "completion_tokens"),
        {**deepseek_usage(), "prompt_cache_miss_tokens": -430},
        {**deepseek_usage(), "prompt_tokens": 495},
        {**deepseek_usage(), "prompt_tokens": None},
        {**deepseek_usage(), "total_tokens": 708},
    ],
)
async def test_missing_or_inconsistent_deepseek_usage_is_unknown(usage: JsonValue) -> None:
    assert await reported(FLASH, usage=usage) is None


async def test_a_response_without_usage_has_unknown_usage() -> None:
    assert await reported(LUNA) is None
    assert await reported(FLASH) is None
