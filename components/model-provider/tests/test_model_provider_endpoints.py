"""Only reviewed origins or explicit loopback fixtures can receive launch credentials."""

from dataclasses import replace

import pytest
from model_provider_fixture import SECRET
from slow_thinker_host import JsonObject, JsonValue
from slow_thinker_model_provider import ProviderEndpoint, endpoint_from_record


@pytest.mark.parametrize(
    "url",
    [
        "http://api.deepseek.com",
        "https://other.example",
        "http://localhost:123/v1",
        "http://127.0.0.1/v1",
        "http://127.0.0.1:0/v1",
        "http://user@127.0.0.1:123/v1",
        "http://127.0.0.1:123/other",
        "https://api.deepseek.com?key=x",
        "https://api.deepseek.com#x",
    ],
)
def test_untrusted_endpoint_is_rejected(url: str) -> None:
    with pytest.raises(ValueError):
        ProviderEndpoint("deepseek", url, SECRET)


@pytest.mark.parametrize(
    "field,value",
    [
        ("api_key", ""),
        ("api_key", SECRET + "\n"),
        ("provider", "other"),
        ("timeout_seconds", float("nan")),
        ("timeout_seconds", True),
        ("close_seconds", 0),
        ("max_response_bytes", 0),
        ("max_response_bytes", True),
    ],
)
def test_invalid_bounds_do_not_echo_secrets(field: str, value: JsonValue) -> None:
    selected = ProviderEndpoint("deepseek", "https://api.deepseek.com", SECRET)
    with pytest.raises(ValueError) as caught:
        replace(selected, **{field: value})
    assert SECRET not in str(caught.value) and SECRET not in repr(selected)


@pytest.mark.parametrize(
    "field,value",
    [
        ("extra", 1),
        ("base_url", 1),
        ("timeout_seconds", "x"),
        ("close_seconds", "x"),
        ("max_response_bytes", True),
    ],
)
def test_trusted_record_checks_types(field: str, value: JsonValue) -> None:
    record: JsonObject = {
        "base_url": "http://127.0.0.1:123/v1",
        "timeout_seconds": 2,
        "close_seconds": 1,
        "max_response_bytes": 1000,
    }
    selected = endpoint_from_record(record, SECRET, "deepseek")
    assert selected.timeout_seconds == 2 and selected.api_key == SECRET
    with pytest.raises(ValueError):
        endpoint_from_record({**record, field: value}, SECRET, "deepseek")


def test_both_official_origins_and_ipv6_fixture_are_supported() -> None:
    assert ProviderEndpoint("openai", "https://api.openai.com/v1", SECRET).provider == "openai"
    assert ProviderEndpoint("deepseek", "http://[::1]:123/v1", SECRET).base_url.endswith("/v1")
