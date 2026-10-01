"""Trusted outgoing endpoints remain explicit loopback bindings with bounded timeouts."""

import pytest
from slow_thinker_host import (
    JsonObject,
    JsonValue,
    McpEndpoint,
    McpResource,
    mcp_endpoint_from_record,
)

RECORD: JsonObject = {
    "url": "http://127.0.0.1:8000/mcp",
    "timeout_seconds": 3,
    "close_seconds": 1,
    "resources": {"worker": {"generate": "worker-generate"}},
}


def test_endpoint_freezes_bindings_and_resolves_only_declared_operations() -> None:
    resources: JsonObject = {"worker": {"generate": "worker-generate"}}
    record: JsonObject = {**RECORD, "resources": resources}
    endpoint = mcp_endpoint_from_record(record)
    resources.clear()
    assert endpoint.alias("worker", "generate") == "worker-generate"
    with pytest.raises(ValueError, match="Missing"):
        endpoint.alias("worker", "other")


@pytest.mark.parametrize(
    "field,value",
    [
        ("extra", 1),
        ("url", 1),
        ("url", "https://127.0.0.1:8000/mcp"),
        ("url", "http://example.test:8000/mcp"),
        ("url", "http://127.0.0.1/mcp"),
        ("url", "http://127.0.0.1:8000/other"),
        ("url", "http://user@127.0.0.1:8000/mcp"),
        ("url", "http://127.0.0.1:8000/mcp?q=1"),
        ("timeout_seconds", "3"),
        ("timeout_seconds", True),
        ("timeout_seconds", 0),
        ("close_seconds", float("inf")),
        ("resources", {"worker": {}}),
        ("resources", {"worker": {"generate": 1}}),
        ("resources", {"worker": {"generate": "platform.report"}}),
    ],
)
def test_invalid_endpoint_is_rejected(field: str, value: JsonValue) -> None:
    with pytest.raises(ValueError):
        mcp_endpoint_from_record({**RECORD, field: value})


def test_duplicate_or_empty_resource_bindings_are_rejected() -> None:
    binding = McpResource("worker", "work", "alias")
    for resources in [(binding, binding), (McpResource("", "work", "alias"),)]:
        with pytest.raises(ValueError):
            McpEndpoint("http://[::1]:123/mcp", 1, 1, resources)
