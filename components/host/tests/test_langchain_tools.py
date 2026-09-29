"""LangChain tools wrap the same filtered, scoped MCP client and preserve errors."""

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_host import (
    Invocation,
    JsonObject,
    McpEndpoint,
    ToolReply,
    managed_langchain_tools,
)

from tooling.tests.mcp_gateway_fixture import GatewayFixture

ENDPOINT = McpEndpoint("http://127.0.0.1:8000/mcp", 2, 1)
SCHEMA: JsonObject = {
    "type": "object",
    "properties": {"text": {"type": "string"}},
    "required": ["text"],
    "additionalProperties": False,
}


async def test_ordinary_structured_tool_keeps_schema_and_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = GatewayFixture()
    fixture.add("allowed", ToolReply({"answer": "yes"}), SCHEMA)
    fixture.install(monkeypatch)
    tools = await managed_langchain_tools(ENDPOINT, Invocation("grant"))
    assert len(tools) == 1 and tools[0].name == "allowed" and tools[0].args_schema == SCHEMA
    assert await tools[0].ainvoke({"text": "question"}) == {"answer": "yes"}
    assert fixture.calls == [("allowed", {"text": "question"}, "Bearer grant")]
    assert len(fixture.clients) == 2 and all(client.is_closed for client in fixture.clients)


async def test_structured_tool_preserves_failure_and_stale_authority(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = GatewayFixture()
    fixture.add("allowed", ToolReply({"reason": "failure"}, True))
    fixture.install(monkeypatch)
    (tool,) = await managed_langchain_tools(ENDPOINT, Invocation("grant"))
    with pytest.raises(MCPError) as captured:
        await tool.ainvoke({})
    assert captured.value.data == {"reason": "failure"}
    fixture.status = 401
    with pytest.raises(MCPError, match="Server returned an error response"):
        await tool.ainvoke({})
    assert len(fixture.calls) == 1


async def test_paginated_discovery_is_explicitly_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = GatewayFixture()
    fixture.cursor = "another-page"
    fixture.install(monkeypatch)
    with pytest.raises(ValueError, match="Paginated"):
        await managed_langchain_tools(ENDPOINT, Invocation("g"))
