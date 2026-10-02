"""Request policy rejects unsupported SDK inputs before charge authorization."""

from dataclasses import replace

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from models.fixtures import arguments, policy, profile


@pytest.mark.parametrize("mode", ["none", "low", "high", "max"])
def test_deepseek_native_reasoning_and_conservative_quote(mode: str) -> None:
    settings = profile()
    native = settings.request(arguments(reasoning_effort=mode, max_completion_tokens=17))
    assert native["thinking"] == {"type": "disabled" if mode == "none" else "enabled"}
    assert native.get("reasoning_effort") == (None if mode == "none" else mode)
    assert native["max_tokens"] == 17 and native["model"] == "deepseek-flash"
    quote = policy().quote(arguments(reasoning_effort=mode, max_completion_tokens=17))
    assert quote.bound == 300_020_400 and quote.tariff_revision == settings.revision.digest
    basis = json_object(decode_json(quote.pricing_json))
    assert basis["input_capacity"] == 1_000_000
    assert "messages" not in json_object(basis["native_request_options"])


@pytest.mark.parametrize(
    "field,value",
    [
        ("model", "other"),
        ("unexpected", 1),
        ("tools", []),
        ("stream", True),
        ("n", 2),
        ("n", True),
        ("reasoning_effort", "medium"),
        ("reasoning_effort", False),
        ("temperature", True),
        ("temperature", "1"),
        ("temperature", 3),
        ("temperature", -1),
        ("max_completion_tokens", 0),
        ("max_completion_tokens", 33),
        ("max_completion_tokens", True),
        ("messages", []),
        ("messages", "x"),
        ("messages", [{"role": "developer", "content": "x"}]),
        ("messages", [{"role": "tool", "content": "x"}]),
        ("messages", [{"role": "user", "content": 1}]),
        ("messages", [{"role": "user", "content": "x", "extra": 1}]),
    ],
)
def test_unsupported_requests_cannot_receive_a_quote(field: str, value: JsonValue) -> None:
    request = json_object(json_object(decode_json(arguments()))["request"])
    with pytest.raises(ValueError):
        policy().quote(encode_json({"request": {**request, field: value}}))


@pytest.mark.parametrize("mode", ["low", "high", "max"])
def test_temperature_requires_nonreasoning_mode(mode: str) -> None:
    with pytest.raises(ValueError):
        policy().quote(arguments(reasoning_effort=mode, temperature=0.5))
    assert profile().request(arguments(temperature=0.5))["temperature"] == 0.5


def test_profile_identity_and_caps_are_checked_independently() -> None:
    settings = profile()
    for selected in ("openai", "deepseek"):
        with pytest.raises(ValueError):
            replace(profile(selected), maximum_output_tokens=1)
    with pytest.raises(ValueError):
        replace(settings, provider="openai")
    with pytest.raises(ValueError):
        policy().quote('{"request": {}, "extra": 1}')


def test_openai_delegation_retains_existing_request_and_quote() -> None:
    native = profile("openai").request(arguments())
    assert native["reasoning_effort"] == "none" and native["store"] is False
    assert native["model"] == "gpt-6-luna"
    quote = policy("openai").quote(arguments())
    assert quote.bound > 0 and quote.tariff_revision == profile("openai").revision.digest
    request: JsonObject = {
        "model": "bound-model",
        "messages": [{"role": "developer", "content": "x"}],
    }
    assert (
        profile("openai").request(encode_json({"request": request}))["messages"]
        == request["messages"]
    )
