"""Independent application and resource request policies must agree at the wire boundary."""

import time

import httpx2
import pytest
from jsonschema import ValidationError
from slow_thinker_host import Invocation
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object
from slow_thinker_openai_model import (
    ModelConfig,
    OpenAIModelHost,
    ProviderEndpoint,
    ProviderTransport,
    effective_operation,
)
from support.native_model import profile, response


def resource(transport: httpx2.AsyncBaseTransport) -> OpenAIModelHost:
    config = ModelConfig("bound-model", "gpt-6-luna", 8, 32)
    return OpenAIModelHost(
        config,
        effective_operation(config),
        ProviderTransport(ProviderEndpoint("https://api.openai.com/v1", "fixture"), transport),
    )


@pytest.mark.parametrize("cap", [None, 1, 32])
async def test_the_resource_transmits_exactly_the_priced_request(cap: int | None) -> None:
    body: JsonObject = {"model": "bound-model", "messages": [{"role": "user", "content": "x"}]}
    if cap is not None:
        body["max_completion_tokens"] = cap
    expected = profile().request(encode_json({"request": body}))

    def handle(request: httpx2.Request) -> httpx2.Response:
        assert json_object(decode_json(request.content.decode())) == expected
        return httpx2.Response(200, json=response())

    result = await resource(httpx2.MockTransport(handle)).invoke(
        "complete", {"request": body}, Invocation("grant", time.monotonic() + 5)
    )
    assert not result.is_error


@pytest.mark.parametrize(
    "key,value",
    [
        ("n", 1.0),
        ("n", True),
        ("max_completion_tokens", 1.0),
        ("max_completion_tokens", 33),
        ("temperature", 0),
        ("stream", True),
        ("model", "unbound"),
    ],
)
async def test_both_sides_reject_options_outside_the_priced_profile(
    key: str, value: JsonValue
) -> None:
    body: JsonObject = {
        "model": "bound-model",
        "messages": [{"role": "user", "content": "x"}],
        key: value,
    }

    def handle(request: httpx2.Request) -> httpx2.Response:
        del request
        pytest.fail("Invalid request reached the provider")

    with pytest.raises(ValueError):
        profile().request(encode_json({"request": body}))
    with pytest.raises((ValueError, ValidationError)):
        await resource(httpx2.MockTransport(handle)).invoke(
            "complete", {"request": body}, Invocation("grant", time.monotonic() + 5)
        )
