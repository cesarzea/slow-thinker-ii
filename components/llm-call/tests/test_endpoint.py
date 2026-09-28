"""Managed clients use loopback bindings, bounded deadlines and deterministic cleanup."""

import asyncio
import time

import pytest
from slow_thinker_host import Invocation, JsonObject
from slow_thinker_llm_call import OpenAIEndpoint, endpoint_from_record


@pytest.mark.parametrize(
    "url",
    [
        "https://api.openai.com/v1",
        "http://localhost/v1",
        "http://127.0.0.1:0/v1",
        "http://127.0.0.1:invalid/v1",
        "http://user@127.0.0.1/v1",
        "http://127.0.0.1/v1?x=1",
        "http://127.0.0.1/v1#fragment",
    ],
)
def test_invalid_binding_is_rejected_at_startup(url: str) -> None:
    with pytest.raises(ValueError):
        OpenAIEndpoint(url, "model", 10, 2)


@pytest.mark.parametrize("seconds", [0, -1, float("inf"), float("nan"), True])
def test_invalid_client_timeouts(seconds: float) -> None:
    with pytest.raises(ValueError):
        OpenAIEndpoint("http://127.0.0.1/v1", "model", seconds, 2)


@pytest.mark.parametrize("cancel", [False, True])
async def test_fresh_client_clamps_timeout_and_closes_on_success_or_cancellation(
    cancel: bool,
) -> None:
    endpoint = OpenAIEndpoint("http://127.0.0.1/v1", "model", 30, 2)
    captured = None
    try:
        async with endpoint.client(Invocation("grant", time.monotonic() + 10)) as client:
            captured = client
            assert isinstance(client.timeout, float) and 0 < client.timeout <= 10
            assert client.api_key == "grant" and client.max_retries == 0
            if cancel:
                raise asyncio.CancelledError
    except asyncio.CancelledError:
        assert cancel
    assert captured is not None and captured.is_closed()


async def test_expired_or_missing_authority_never_creates_client() -> None:
    endpoint = OpenAIEndpoint("http://127.0.0.1/v1", "model", 30, 2)
    with pytest.raises(TimeoutError):
        async with endpoint.client(Invocation("grant", time.monotonic() - 1)):
            pytest.fail("Expired invocation was accepted")
    with pytest.raises(ValueError):
        async with endpoint.client(Invocation("")):
            pytest.fail("Missing grant was accepted")


@pytest.mark.parametrize(
    "record",
    [
        {},
        {"base_url": 1, "model": "model", "timeout_seconds": 10, "close_seconds": 2},
        {
            "base_url": "http://127.0.0.1/v1",
            "model": "model",
            "timeout_seconds": "10",
            "close_seconds": 2,
        },
    ],
)
def test_client_record_requires_exact_fields_and_types(record: JsonObject) -> None:
    with pytest.raises(ValueError):
        endpoint_from_record(record)
