"""Worker schema mismatches stop routing; local references survive composition output."""

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    GRANT_META,
    PROTOCOL_VERSION,
    JsonObject,
    McpEndpoint,
    McpResource,
    ToolReply,
    create_server,
)
from slow_thinker_routed_call import RoutedCallHost

from tooling.tests.mcp_gateway_fixture import GatewayFixture

CONFIG: JsonObject = {
    "input_schema": {"type": "object"},
    "worker_operation": "work",
    "worker_output_schema": {
        "type": "object",
        "$defs": {"answer": {"type": "integer"}},
        "properties": {"answer": {"$ref": "#/$defs/answer"}},
        "required": ["answer"],
    },
    "router_input_pointer": "/answer",
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


@pytest.mark.parametrize("valid", [True, False])
async def test_worker_schema_is_enforced_and_scoped_when_nested(
    monkeypatch: pytest.MonkeyPatch, valid: bool
) -> None:
    fixture = GatewayFixture()
    fixture.add("work", ToolReply({"answer": 7 if valid else "wrong"}))
    fixture.add("route", ToolReply({"port": "done"}))
    fixture.install(monkeypatch)
    (operation,) = RoutedCallHost.describe(CONFIG)
    host = RoutedCallHost(CONFIG, operation, ENDPOINT)
    async with Client(create_server(host, "routed", "1"), mode=PROTOCOL_VERSION) as client:
        if valid:
            result = await client.call_tool("invoke", {}, meta={GRANT_META: "grant"})
            assert result.structured_content == {
                "status": "succeeded",
                "port": "done",
                "value": {"answer": 7},
            }
            assert len(fixture.calls) == 2
        else:
            with pytest.raises(MCPError) as captured:
                await client.call_tool("invoke", {}, meta={GRANT_META: "grant"})
            assert captured.value.data["stage"] == "worker" and len(fixture.calls) == 1
