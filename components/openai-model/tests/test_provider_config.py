"""Only trusted, bounded provider profiles can become ready."""

from dataclasses import replace

import pytest
from slow_thinker_host import JsonObject, JsonValue
from slow_thinker_openai_model import (
    ModelConfig,
    ProviderEndpoint,
    endpoint_from_record,
    parse_config,
)


@pytest.mark.parametrize(
    "url",
    [
        "http://api.openai.com/v1",
        "https://other.example/v1",
        "http://localhost:123/v1",
        "http://127.0.0.1/v1",
        "http://127.0.0.1:0/v1",
        "http://user@127.0.0.1:123/v1",
        "http://127.0.0.1:123/elsewhere",
        "https://api.openai.com/v1?key=other",
    ],
)
def test_upstream_destinations_cannot_be_redirected_by_graph_data(url: str) -> None:
    with pytest.raises(ValueError):
        ProviderEndpoint(url, "fixture")


@pytest.mark.parametrize("fault", ["key", "newline", "timeout", "close", "limit", "boolean"])
def test_invalid_provider_bounds_and_credentials_are_rejected_without_echo(fault: str) -> None:
    endpoint = ProviderEndpoint("https://api.openai.com/v1", "fixture-secret")
    with pytest.raises(ValueError) as caught:
        if fault in {"key", "newline"}:
            replace(endpoint, api_key="" if fault == "key" else "fixture-secret\n")
        elif fault == "timeout":
            replace(endpoint, timeout_seconds=float("nan"))
        elif fault == "close":
            replace(endpoint, close_seconds=0)
        elif fault == "limit":
            replace(endpoint, max_response_bytes=0)
        else:
            replace(endpoint, max_response_bytes=True)
    assert "fixture-secret" not in str(caught.value) and "fixture-secret" not in repr(endpoint)


def test_bootstrap_endpoint_parser_keeps_secret_separate() -> None:
    record: JsonObject = {
        "base_url": "http://127.0.0.1:123/v1",
        "timeout_seconds": 2,
        "close_seconds": 1,
        "max_response_bytes": 1000,
    }
    endpoint = endpoint_from_record(record, "fixture-secret")
    assert endpoint.api_key == "fixture-secret" and "fixture-secret" not in repr(endpoint)
    assert endpoint.timeout_seconds == 2 and endpoint.close_seconds == 1
    for field, value in (
        ("unknown", 1),
        ("base_url", 1),
        ("timeout_seconds", "x"),
        ("close_seconds", "x"),
        ("max_response_bytes", True),
    ):
        invalid: JsonObject = {**record, field: value}
        with pytest.raises(ValueError):
            endpoint_from_record(invalid, "fixture-secret")


@pytest.mark.parametrize(
    "field,value",
    [
        ("model_alias", ""),
        ("model", False),
        ("default_output_tokens", 0),
        ("maximum_output_tokens", 1),
        ("default_output_tokens", True),
        ("maximum_output_tokens", "32"),
        ("extra", 1),
    ],
)
def test_invalid_resource_configuration_is_rejected(field: str, value: JsonValue) -> None:
    config: JsonObject = {
        "model_alias": "bound",
        "model": "model",
        "default_output_tokens": 8,
        "maximum_output_tokens": 32,
    }
    assert parse_config(config) == ModelConfig("bound", "model", 8, 32)
    with pytest.raises(ValueError):
        parse_config({**config, field: value})
