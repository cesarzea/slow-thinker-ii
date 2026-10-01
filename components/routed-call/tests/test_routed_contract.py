"""Schemas, bindings and JSON pointers are validated without changing worker semantics."""

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    Invocation,
    JsonObject,
    JsonValue,
    McpEndpoint,
    McpResource,
    Operation,
    ToolReply,
)
from slow_thinker_routed_call import RoutedCall, RoutedCallHost, parse_config

from tooling.tests.mcp_gateway_fixture import GatewayFixture

CONFIG: JsonObject = {
    "input_schema": {"type": "object"},
    "worker_operation": "work",
    "worker_output_schema": {"type": "object"},
    "router_input_pointer": "",
    "outputs": ["done"],
}
ENDPOINT = McpEndpoint(
    "http://127.0.0.1:1/mcp",
    3,
    1,
    (
        McpResource("worker", "work", "work"),
        McpResource("router", "route", "route"),
    ),
)


@pytest.mark.parametrize(
    "pointer,expected", [("", {"a/b": {"~key": [False, True]}}), ("/a~1b/~0key/1", True)]
)
async def test_json_pointer_preserves_escaped_names_and_arrays(
    monkeypatch: pytest.MonkeyPatch, pointer: str, expected: JsonValue
) -> None:
    fixture = GatewayFixture()
    fixture.add("work", ToolReply({"a/b": {"~key": [False, True]}}))
    fixture.add("route", ToolReply({"port": "done"}))
    fixture.install(monkeypatch)
    config = {**CONFIG, "router_input_pointer": pointer}
    (operation,) = RoutedCallHost.describe(config)
    host = RoutedCallHost(config, operation, ENDPOINT)
    assert host.operations() == (operation,)
    assert (await host.invoke("invoke", {}, Invocation("g"))).value["port"] == "done"
    assert fixture.calls[1][1] == {"value": expected}


@pytest.mark.parametrize(
    "pointer", ["/array/01", "/array/-", "/array/2", "/absent", "/array/0/key"]
)
async def test_unresolvable_pointer_stops_before_router(
    monkeypatch: pytest.MonkeyPatch, pointer: str
) -> None:
    fixture = GatewayFixture()
    fixture.add("work", ToolReply({"array": [1]}))
    fixture.add("route", ToolReply({"port": "done"}))
    fixture.install(monkeypatch)
    with pytest.raises(MCPError) as captured:
        await RoutedCall(
            parse_config({**CONFIG, "router_input_pointer": pointer}), ENDPOINT
        ).invoke({}, Invocation("g"))
    assert captured.value.data["stage"] == "extraction" and len(fixture.calls) == 1


@pytest.mark.parametrize(
    "field,value",
    [
        ("extra", None),
        ("worker_operation", ""),
        ("router_input_pointer", "/bad~2"),
        ("router_input_pointer", "bad"),
        ("outputs", []),
        ("outputs", "done"),
        ("outputs", [1]),
        ("outputs", ["done", "done"]),
        ("input_schema", {}),
        ("worker_output_schema", {"type": "string"}),
    ],
)
def test_invalid_configuration_fails(field: str, value: JsonValue) -> None:
    with pytest.raises(ValueError):
        parse_config({**CONFIG, field: value})


async def test_host_requires_exact_schemas_operations_and_resource_bindings() -> None:
    (operation,) = RoutedCallHost.describe(CONFIG)
    with pytest.raises(ValueError, match="schemas"):
        RoutedCallHost(CONFIG, Operation("invoke", {}, {}), ENDPOINT)
    with pytest.raises(ValueError, match="Missing MCP"):
        RoutedCall(parse_config(CONFIG), McpEndpoint(ENDPOINT.url, 1, 1))
    with pytest.raises(ValueError, match="Unsupported"):
        await RoutedCallHost(CONFIG, operation, ENDPOINT).invoke("other", {}, Invocation("g"))
