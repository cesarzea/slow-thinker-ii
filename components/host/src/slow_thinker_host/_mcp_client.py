"""Fresh ordinary MCP clients carry authority only to the local platform gateway."""

import asyncio
import math
import time
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager

import httpx2
from mcp import Client, types
from mcp.client.streamable_http import streamable_http_client

from ._contracts import Invocation
from ._mcp_endpoint import McpEndpoint
from ._server import PROTOCOL_VERSION


def _deadline(endpoint: McpEndpoint, invocation: Invocation) -> float:
    if not invocation.grant:
        raise ValueError("Invocation authority is required")
    end = time.monotonic() + endpoint.timeout_seconds
    if invocation.deadline is not None:
        if isinstance(invocation.deadline, bool) or not math.isfinite(invocation.deadline):
            raise ValueError("Invalid invocation deadline")
        end = min(end, invocation.deadline)
    if end <= time.monotonic():
        raise TimeoutError("Invocation deadline expired before MCP client creation")
    return end


async def _open_client(
    stack: AsyncExitStack, endpoint: McpEndpoint, invocation: Invocation, end: float
) -> Client:
    http = await stack.enter_async_context(
        httpx2.AsyncClient(
            headers={"Authorization": f"Bearer {invocation.grant}"},
            timeout=max(0.001, end - time.monotonic()),
            trust_env=False,
            follow_redirects=False,
        )
    )
    client = Client(
        streamable_http_client(endpoint.url, http_client=http),
        mode=PROTOCOL_VERSION,
        read_timeout_seconds=max(0.001, end - time.monotonic()),
        cache=None,
    )
    return await stack.enter_async_context(client)


async def _discover(client: Client) -> None:
    discovered = await client.session.send_request(types.DiscoverRequest(), types.DiscoverResult)
    if PROTOCOL_VERSION not in discovered.supported_versions:
        raise ValueError("Platform does not support the pinned MCP protocol")
    capabilities = discovered.capabilities.model_dump(exclude_none=True, by_alias=True)
    if set(capabilities) != {"tools"}:
        raise ValueError("Platform advertises unsupported MCP capabilities")


@asynccontextmanager
async def managed_mcp_client(
    endpoint: McpEndpoint, invocation: Invocation
) -> AsyncIterator[Client]:
    end = _deadline(endpoint, invocation)
    stack = AsyncExitStack()
    try:
        async with asyncio.timeout_at(end):
            client = await _open_client(stack, endpoint, invocation, end)
            await _discover(client)
            yield client
    finally:
        async with asyncio.timeout(endpoint.close_seconds):
            await stack.aclose()
