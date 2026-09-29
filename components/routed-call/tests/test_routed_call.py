"""Normal MCP worker/router calls preserve payloads, ordering and failed stages."""

import asyncio

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, JsonObject, McpEndpoint, McpResource, ToolReply
from slow_thinker_routed_call import RoutedCall, parse_config

from tooling.tests.mcp_gateway_fixture import GatewayFixture

CONFIG: JsonObject = {
    "input_schema": {"type": "object"},
    "worker_operation": "generate",
    "worker_output_schema": {"type": "object"},
    "router_input_pointer": "/value",
    "outputs": ["accept", "revise"],
}
ENDPOINT = McpEndpoint(
    "http://127.0.0.1:8000/mcp",
    5,
    1,
    (
        McpResource("worker", "generate", "worker-generate"),
        McpResource("router", "route", "router-route"),
    ),
)


def gateway(monkeypatch: pytest.MonkeyPatch) -> GatewayFixture:
    fixture = GatewayFixture()
    fixture.add(
        "worker-generate",
        ToolReply({"status": "ok", "format": "json", "value": {"accepted": True}}),
    )
    fixture.add("router-route", ToolReply({"port": "accept"}))
    fixture.install(monkeypatch)
    return fixture


async def test_composition_preserves_normal_worker_envelope_and_scoped_calls(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = gateway(monkeypatch)
    result = await RoutedCall(parse_config(CONFIG), ENDPOINT).invoke(
        {"problem": "task"}, Invocation("grant")
    )
    assert result == ToolReply(
        {"status": "succeeded", "port": "accept", "value": fixture.replies["worker-generate"].value}
    )
    assert fixture.calls == [
        ("worker-generate", {"problem": "task"}, "Bearer grant"),
        ("router-route", {"value": {"accepted": True}}, "Bearer grant"),
    ]
    assert all(str(request.url) == ENDPOINT.url for request in fixture.requests)


@pytest.mark.parametrize(
    "stage,worker,router,pointer",
    [
        ("worker", ToolReply({"error": "bad"}, True), ToolReply({"port": "accept"}), "/value"),
        ("extraction", ToolReply({}), ToolReply({"port": "accept"}), "/missing"),
        ("router", ToolReply({"value": {}}), ToolReply({"error": "bad"}, True), "/value"),
        ("router", ToolReply({"value": {}}), ToolReply({"port": "other"}), "/value"),
        ("router", ToolReply({"value": {}}), ToolReply({"port": "accept", "extra": 1}), "/value"),
    ],
)
async def test_failed_stage_publishes_no_port_and_never_retries(
    monkeypatch: pytest.MonkeyPatch, stage: str, worker: ToolReply, router: ToolReply, pointer: str
) -> None:
    fixture = gateway(monkeypatch)
    fixture.replies.update({"worker-generate": worker, "router-route": router})
    config = parse_config({**CONFIG, "router_input_pointer": pointer})
    with pytest.raises(MCPError) as captured:
        await RoutedCall(config, ENDPOINT).invoke({}, Invocation("grant"))
    assert captured.value.code == -32603
    assert captured.value.data["stage"] == stage and "port" not in captured.value.data
    assert [call[0] for call in fixture.calls] == (
        ["worker-generate", "router-route"] if stage == "router" else ["worker-generate"]
    )


async def test_invalid_input_never_opens_managed_client(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    config = parse_config({**CONFIG, "input_schema": {"type": "object", "required": ["problem"]}})
    with pytest.raises(MCPError) as captured:
        await RoutedCall(config, ENDPOINT).invoke({}, Invocation("grant"))
    assert captured.value.data["stage"] == "input" and not fixture.clients


async def test_cancellation_propagates_without_router_call(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = gateway(monkeypatch)
    fixture.block = True
    task = asyncio.create_task(
        RoutedCall(parse_config(CONFIG), ENDPOINT).invoke({}, Invocation("g"))
    )
    await asyncio.wait_for(fixture.started.wait(), 2)
    task.cancel()
    with pytest.raises(asyncio.CancelledError):
        await task
    assert len(fixture.calls) == 1 and all(client.is_closed for client in fixture.clients)
