"""Embedding authored schemas preserves their local-reference scope."""

import pytest
from mcp import Client
from mcp.shared.exceptions import MCPError
from slow_thinker_host import GRANT_META, PROTOCOL_VERSION, JsonObject, create_server
from slow_thinker_redirector import RedirectorHost

SCHEMA: JsonObject = {
    "$defs": {
        "review": {
            "type": "object",
            "properties": {"accepted": {"type": "boolean"}},
            "required": ["accepted"],
        }
    },
    "$ref": "#/$defs/review",
}


async def test_authored_local_reference_remains_local_after_embedding() -> None:
    config: JsonObject = {
        "outputs": ["accept", "revise"],
        "selector": "example_grounded_review:choose",
        "input_schema": SCHEMA,
    }
    (operation,) = RedirectorHost.describe(config)
    host = RedirectorHost(config, operation)
    async with Client(create_server(host, "redirector", "1"), mode=PROTOCOL_VERSION) as client:
        reply = await client.call_tool(
            "route", {"value": {"accepted": True}}, meta={GRANT_META: "g"}
        )
        assert reply.structured_content == {"port": "accept"}
        with pytest.raises(MCPError):
            await client.call_tool("route", {"value": {"accepted": "true"}}, meta={GRANT_META: "g"})
