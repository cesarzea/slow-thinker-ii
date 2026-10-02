"""Schemas, pointers, collisions and bindings fail explicitly before silent changes."""

import pytest
from context_case import CONFIG, ENDPOINT, gateway
from mcp.shared.exceptions import MCPError
from slow_thinker_contextual_call import ContextualCall, ContextualCallHost
from slow_thinker_host import Invocation, JsonObject, JsonValue, McpEndpoint, McpResource, Operation


@pytest.mark.parametrize(
    "field,value",
    [
        ("extra", None),
        ("worker_operation", 1),
        ("input_schema", {}),
        ("worker_output_schema", {"type": "string"}),
        ("memory_read", 1),
        ("result_pointer", "/a~2"),
        ("memory_key", "é" * 129),
        ("calculation_field", "memory"),
        ("input_schema", {"type": "object", "$ref": "https://invalid"}),
    ],
)
def test_bad_configuration_is_rejected(field: str, value: JsonValue) -> None:
    with pytest.raises(ValueError):
        ContextualCallHost.describe({**CONFIG, field: value})


@pytest.mark.parametrize(
    "pointer", ["/absent", "/expression/0", "/array/01", "/array/9", "/array/-"]
)
async def test_invalid_expression_pointer_does_not_call_calculator(
    monkeypatch: pytest.MonkeyPatch, pointer: str
) -> None:
    fixture = gateway(monkeypatch)
    with pytest.raises(MCPError) as caught:
        await ContextualCall({**CONFIG, "expression_pointer": pointer}, ENDPOINT).invoke(
            {"expression": "1+2", "array": [1]}, Invocation("g")
        )
    assert caught.value.data["stage"] == "calculate"
    assert [item[0] for item in fixture.calls] == ["memory-get"]


async def test_escaped_pointer_and_result_selection(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    config = {**CONFIG, "expression_pointer": "/a~1b/~0key/0", "result_pointer": ""}
    host = ContextualCallHost(config, ContextualCallHost.describe(config)[0], ENDPOINT)
    assert host.operations() == ContextualCallHost.describe(config)
    await host.invoke("invoke", {"a/b": {"~key": ["1+2"]}}, Invocation("g"))
    assert fixture.calls[-1][1]["value"] == fixture.replies["worker-work"].value
    with pytest.raises(ValueError):
        await host.invoke("other", {}, Invocation("g"))
    with pytest.raises(ValueError):
        ContextualCallHost(config, Operation("invoke", {}, {}), ENDPOINT)


@pytest.mark.parametrize(
    "arguments,stage",
    [
        ({"memory": 1}, "memory_get"),
        ({"expression": 1}, "calculate"),
        ({"expression": "1+2", "calculation": 1}, "calculate"),
    ],
)
async def test_invalid_context_never_overwrites_inputs(
    monkeypatch: pytest.MonkeyPatch, arguments: JsonObject, stage: str
) -> None:
    gateway(monkeypatch)
    with pytest.raises(MCPError) as caught:
        await ContextualCall(CONFIG, ENDPOINT).invoke(arguments, Invocation("g"))
    assert caught.value.data["stage"] == stage


def test_missing_and_unsupported_bindings() -> None:
    with pytest.raises(ValueError, match="Missing MCP"):
        ContextualCall(CONFIG, McpEndpoint(ENDPOINT.url, 1, 1))
    with pytest.raises(ValueError, match="Unsupported"):
        ContextualCall(CONFIG, McpEndpoint(ENDPOINT.url, 1, 1, (McpResource("unknown", "x", "x"),)))


async def test_invalid_input_does_not_open_transport(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    config: JsonObject = {**CONFIG, "input_schema": {"type": "object", "required": ["task"]}}
    with pytest.raises(MCPError) as caught:
        await ContextualCall(config, ENDPOINT).invoke({}, Invocation("g"))
    assert caught.value.data["stage"] == "input" and not fixture.clients
