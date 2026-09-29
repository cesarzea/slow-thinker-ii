"""Optional LangChain tool bindings over the same supported, scoped MCP client."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TYPE_CHECKING

from mcp.shared.exceptions import MCPError

from ._contracts import Invocation
from ._json import JsonObject, json_object
from ._mcp_client import managed_mcp_client
from ._mcp_endpoint import McpEndpoint

if TYPE_CHECKING:
    from langchain_core.tools import StructuredTool


def _coroutine(
    endpoint: McpEndpoint, invocation: Invocation, alias: str
) -> Callable[..., Awaitable[JsonObject]]:
    async def call(**arguments: object) -> JsonObject:
        async with managed_mcp_client(endpoint, invocation) as client:
            reply = await client.call_tool(alias, json_object(arguments))
        value = json_object(reply.structured_content)
        if reply.is_error:
            raise MCPError(code=-32603, message="managed_tool_failed", data=value)
        return value

    return call


async def managed_langchain_tools(
    endpoint: McpEndpoint, invocation: Invocation
) -> tuple[StructuredTool, ...]:
    """Discover permitted tools and bind each to this invocation without client reuse."""
    from langchain_core.tools import StructuredTool

    async with managed_mcp_client(endpoint, invocation) as client:
        listing = await client.list_tools()
    if listing.next_cursor is not None:
        raise ValueError("Paginated platform tool discovery is unsupported")
    return tuple(
        StructuredTool(
            name=tool.name,
            description=tool.description or tool.name,
            args_schema=json_object(tool.input_schema),
            coroutine=_coroutine(endpoint, invocation, tool.name),
        )
        for tool in listing.tools
    )
