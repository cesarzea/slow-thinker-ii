"""One authenticated attempt to the configured origin, within the smaller time budget."""

import asyncio
import time
from datetime import UTC, datetime

import httpx
import pytest
from slow_thinker_ii.adapters.providers import HttpProvider, ProviderEndpoint
from slow_thinker_ii.contracts import JsonObject
from support.examples import FLASH, LUNA

from .fixtures import (
    SECRET,
    Exchanges,
    assert_timed,
    chat,
    completion,
    error_of,
    http_provider,
    model,
)


@pytest.mark.parametrize("status", [200, 400, 401, 403, 404, 422, 429, 500, 503])
async def test_one_attempt_with_bearer_authentication_keeps_the_status(status: int) -> None:
    refused: JsonObject = {"error": {"message": "Refused.", "type": "x", "code": "fixture"}}
    body = completion() if status == 200 else refused
    provider, exchanges = http_provider(lambda request: httpx.Response(status, json=body))
    before = datetime.now(UTC)
    reply = await provider.complete(model(FLASH), chat(FLASH), 30)
    [request] = exchanges.requests
    assert (request.method, str(request.url)) == (
        "POST",
        "https://api.deepseek.com/chat/completions",
    )
    assert request.headers["authorization"] == f"Bearer {SECRET}"
    assert request.headers["content-type"] == "application/json"
    assert request.headers["accept-encoding"] == "identity"
    assert_timed(reply, before)
    if status == 200:
        assert (reply.status, reply.body) == (200, body)
    else:
        message = f"The provider answered with HTTP {status}: Refused. (fixture)"
        assert (reply.status, reply.usage) == (502, None)
        assert error_of(reply) == {
            "code": "provider_error",
            "message": message,
            "type": "provider_error",
        }


@pytest.mark.parametrize(
    ("base_url", "url"),
    [
        ("https://api.openai.com/v1", "https://api.openai.com/v1/chat/completions"),
        ("http://127.0.0.1:8080/v1", "http://127.0.0.1:8080/v1/chat/completions"),
    ],
)
async def test_only_the_configured_origin_is_contacted(base_url: str, url: str) -> None:
    exchanges = Exchanges(lambda request: httpx.Response(200, json=completion()))
    endpoint = ProviderEndpoint("openai", base_url, SECRET)
    provider = HttpProvider({"openai": endpoint}, exchanges.transport())
    reply = await provider.complete(model(LUNA), chat(LUNA), 30)
    assert reply.status == 200 and [str(item.url) for item in exchanges.requests] == [url]


async def test_a_redirect_is_not_followed() -> None:
    location = {"location": "https://other.example/chat/completions"}
    provider, exchanges = http_provider(lambda request: httpx.Response(307, headers=location))
    reply = await provider.complete(model(LUNA), chat(LUNA), 30)
    assert reply.status == 502 and len(exchanges.requests) == 1
    assert error_of(reply)["message"] == "The provider answered with HTTP 307: no details."


async def test_an_unconfigured_provider_is_a_provider_error() -> None:
    provider, exchanges = http_provider(lambda request: httpx.Response(200, json=completion()))
    reply = await provider.complete(model(LUNA, provider="simulated"), chat(LUNA), 30)
    assert reply.status == 502 and not exchanges.requests
    assert error_of(reply)["message"] == "No provider endpoint is configured for “simulated”."


@pytest.mark.parametrize("timeout_s", [0.0, -1.0, float("nan")])
async def test_no_time_left_is_a_timeout_without_a_request(timeout_s: float) -> None:
    provider, exchanges = http_provider(lambda request: httpx.Response(200, json=completion()))
    reply = await provider.complete(model(LUNA), chat(LUNA), timeout_s)
    assert reply.status == 504 and not exchanges.requests
    assert error_of(reply) == {
        "code": "provider_timeout",
        "message": "No time was left for the provider call.",
        "type": "timeout_error",
    }


async def slow(request: httpx.Request) -> httpx.Response:
    del request
    await asyncio.sleep(5)
    return httpx.Response(200, json=completion())


@pytest.mark.parametrize(("configured", "remaining"), [(0.05, 30.0), (30.0, 0.05)])
async def test_the_smaller_of_both_timeouts_applies(configured: float, remaining: float) -> None:
    provider, exchanges = http_provider(slow, timeout=configured)
    started = time.monotonic()
    reply = await provider.complete(model(FLASH), chat(FLASH), remaining)
    assert time.monotonic() - started < 2 and len(exchanges.requests) == 1
    assert (reply.status, reply.usage) == (504, None)
    assert error_of(reply) == {
        "code": "provider_timeout",
        "message": "The provider did not answer within 0.05 seconds.",
        "type": "timeout_error",
    }
