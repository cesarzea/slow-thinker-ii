"""Bounded transport injection preserves the real standard MCP client wire."""

import pytest
from slow_thinker_host import JsonObject, McpEndpoint, McpResource, ToolReply

from tooling.tests.mcp_gateway_fixture import GatewayFixture

CONFIG: JsonObject = {
    "input_schema": {"type": "object"},
    "worker_operation": "work",
    "worker_output_schema": {"type": "object"},
    "calculation_enabled": True,
    "memory_read": True,
    "memory_write": True,
    "result_pointer": "/value",
}
ENDPOINT = McpEndpoint(
    "http://127.0.0.1:8000/mcp",
    3,
    1,
    (
        McpResource("worker", "work", "worker-work"),
        McpResource("calculator", "calculate", "calculator-calculate"),
        McpResource("memory", "get", "memory-get"),
        McpResource("memory", "put", "memory-put"),
    ),
)


def gateway(monkeypatch: pytest.MonkeyPatch) -> GatewayFixture:
    fixture = GatewayFixture()
    fixture.add("memory-get", ToolReply({"found": True, "value": {"remembered": 1}, "version": 1}))
    fixture.add("calculator-calculate", ToolReply({"expression": "1+2", "value": "3"}))
    fixture.add("worker-work", ToolReply({"value": {"n": 9007199254740993}}))
    fixture.add("memory-put", ToolReply({"version": 2}))
    fixture.install(monkeypatch)
    return fixture
