"""MCP clients of `/mcp`: the SDK client as the host SDK configures it, and raw requests."""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import httpx2
from fastapi import FastAPI
from mcp import Client, types
from mcp.client.streamable_http import streamable_http_client
from slow_thinker_ii.contracts import JsonObject

from .http_harness import BASE

PROTOCOL = "2026-07-28"
REPORT_TOOL = "platform.report"


@asynccontextmanager
async def report_client(app: FastAPI, grant: str) -> AsyncGenerator[Client]:
    """The host SDK's report client: bearer grant, no redirects, pinned revision, no cache."""
    async with httpx2.AsyncClient(
        transport=httpx2.ASGITransport(app=app),
        headers={"Authorization": f"Bearer {grant}"},
        trust_env=False,
        follow_redirects=False,
    ) as http:
        transport = streamable_http_client(f"{BASE}/mcp", http_client=http)
        async with Client(transport, mode=PROTOCOL, cache=None) as client:
            yield client


async def call(
    client: Client, arguments: JsonObject, name: str = REPORT_TOOL
) -> types.CallToolResult:
    """One tool request, sent exactly as the host SDK sends a report."""
    request = types.CallToolRequest(
        params=types.CallToolRequestParams(name=name, arguments=dict(arguments))
    )
    return await client.session.send_request(request, types.CallToolResult)


def tool_error(result: types.CallToolResult) -> str:
    """The code of a tool error, whose only content is the text `{"code", "message"}`."""
    [content] = result.content
    assert result.is_error and result.structured_content is None
    assert isinstance(content, types.TextContent)
    return json.loads(content.text)["code"]


def raw_call(arguments: str) -> bytes:
    """A protocol 2026-07-28 `tools/call` of the report tool with literal JSON arguments."""
    meta = (
        f'{{"io.modelcontextprotocol/protocolVersion": "{PROTOCOL}", '
        '"io.modelcontextprotocol/clientCapabilities": {}}'
    )
    params = f'{{"name": "{REPORT_TOOL}", "arguments": {arguments}, "_meta": {meta}}}'
    return f'{{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {params}}}'.encode()


def raw_headers(grant: str) -> dict[str, str]:
    return {
        "authorization": f"Bearer {grant}",
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
        "mcp-protocol-version": PROTOCOL,
        "mcp-method": "tools/call",
        "mcp-name": REPORT_TOOL,
    }
