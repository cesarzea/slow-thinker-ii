"""Only reviewed origins or explicit loopback fixtures can receive provider credentials."""

from dataclasses import replace

import pytest
from slow_thinker_ii.adapters.providers import HttpProvider, ProviderEndpoint

from .fixtures import DEEPSEEK_URL, OPENAI_URL, SECRET


@pytest.mark.parametrize(
    "url",
    [
        "http://api.deepseek.com",
        "https://api.deepseek.com/v1",
        "https://api.openai.com/v1",
        "https://other.example",
        "http://localhost:123/v1",
        "https://127.0.0.1:123/v1",
        "http://127.0.0.1/v1",
        "http://127.0.0.1:0/v1",
        "http://127.0.0.1:123/other",
        "http://user@127.0.0.1:123/v1",
        f"http://user:{SECRET}@127.0.0.1:123/v1",
        "https://api.deepseek.com?key=x",
        "https://api.deepseek.com#x",
    ],
)
def test_an_untrusted_endpoint_is_rejected_without_echoing_it(url: str) -> None:
    with pytest.raises(ValueError) as caught:
        ProviderEndpoint("deepseek", url, SECRET)
    assert url not in str(caught.value) and SECRET not in str(caught.value)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("api_key", ""),
        ("api_key", SECRET + "\n"),
        ("api_key", "key with spaces"),
        ("provider", "other"),
        ("timeout_seconds", float("nan")),
        ("timeout_seconds", float("inf")),
        ("timeout_seconds", 0),
        ("timeout_seconds", -1),
        ("timeout_seconds", True),
        ("max_response_bytes", 0),
        ("max_response_bytes", 1.5),
        ("max_response_bytes", True),
    ],
)
def test_invalid_settings_never_echo_the_credential(field: str, value: object) -> None:
    selected = ProviderEndpoint("deepseek", DEEPSEEK_URL, SECRET)
    with pytest.raises(ValueError) as caught:
        replace(selected, **{field: value})
    assert SECRET not in str(caught.value) and SECRET not in repr(selected)


@pytest.mark.parametrize(
    ("provider", "base_url", "url"),
    [
        ("openai", OPENAI_URL, "https://api.openai.com/v1/chat/completions"),
        ("openai", OPENAI_URL + "/", "https://api.openai.com/v1/chat/completions"),
        ("deepseek", DEEPSEEK_URL, "https://api.deepseek.com/chat/completions"),
        ("deepseek", "http://127.0.0.1:8080/v1", "http://127.0.0.1:8080/v1/chat/completions"),
        ("openai", "http://[::1]:123/v1/", "http://[::1]:123/v1/chat/completions"),
    ],
)
def test_reviewed_origins_and_loopback_fixtures_are_the_only_urls(
    provider: str, base_url: str, url: str
) -> None:
    endpoint = ProviderEndpoint("openai", OPENAI_URL, SECRET)
    endpoint = replace(endpoint, provider=provider, base_url=base_url)
    assert endpoint.url == url
    assert (endpoint.timeout_seconds, endpoint.max_response_bytes) == (120, 524_288)


def test_an_endpoint_serves_only_the_provider_it_is_configured_as() -> None:
    endpoint = ProviderEndpoint("deepseek", DEEPSEEK_URL, SECRET)
    with pytest.raises(ValueError) as caught:
        HttpProvider({"openai": endpoint})
    assert SECRET not in str(caught.value)
