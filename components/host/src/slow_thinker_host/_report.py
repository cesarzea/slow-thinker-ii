"""One `platform.report` call over MCP HTTP, authenticated by the invocation grant."""

import httpx2
from mcp import Client, types
from mcp.client.streamable_http import streamable_http_client

from ._json import JsonObject
from ._protocol import PROTOCOL_VERSION, REPORT_TOOL


async def send_report(url: str, grant: str, arguments: JsonObject, seconds: float) -> None:
    """Send exactly one tool request; any transport or tool failure raises."""
    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {grant}"},
        timeout=seconds,
        trust_env=False,
        follow_redirects=False,
    ) as http:
        transport = streamable_http_client(url, http_client=http)
        async with Client(transport, mode=PROTOCOL_VERSION, cache=None) as client:
            request = types.CallToolRequest(
                params=types.CallToolRequestParams(name=REPORT_TOOL, arguments=arguments)
            )
            result = await client.session.send_request(request, types.CallToolResult)
    if result.is_error:
        raise ValueError("The platform rejected the report")
