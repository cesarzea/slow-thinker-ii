"""Standard MCP HTTP calls use fresh scoped credentials and explicit discovery."""

import time

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, McpEndpoint, ToolReply, managed_mcp_client

from tooling.tests.mcp_gateway_fixture import GatewayFixture

ENDPOINT = McpEndpoint("http://127.0.0.1:8000/mcp", 2, 1)


async def test_managed_client_is_fresh_and_runs_real_wire_discovery(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = GatewayFixture()
    fixture.add("echo", ToolReply({"value": 7}))
    fixture.install(monkeypatch)
    for grant in ("first", "second"):
        async with managed_mcp_client(ENDPOINT, Invocation(grant)) as client:
            listed = await client.list_tools()
            assert [tool.name for tool in listed.tools] == ["echo"]
            assert (await client.call_tool("echo", {})).structured_content == {"value": 7}
    assert [call[2] for call in fixture.calls] == ["Bearer first", "Bearer second"]
    assert len(fixture.clients) == 2 and all(client.is_closed for client in fixture.clients)
    assert sum(b'"server/discover"' in req.content for req in fixture.requests) == 2


@pytest.mark.parametrize(
    "invocation",
    [Invocation(""), Invocation("g", 0), Invocation("g", float("nan")), Invocation("g", True)],
)
async def test_invalid_authority_or_deadline_never_creates_client(
    monkeypatch: pytest.MonkeyPatch, invocation: Invocation
) -> None:
    fixture = GatewayFixture()
    fixture.install(monkeypatch)
    with pytest.raises((ValueError, TimeoutError)):
        async with managed_mcp_client(ENDPOINT, invocation):
            pytest.fail("Invalid invocation reached client")
    assert not fixture.clients


@pytest.mark.parametrize("unsupported", ["version", "capabilities"])
async def test_unsupported_discovery_fails_without_business_call(
    monkeypatch: pytest.MonkeyPatch, unsupported: str
) -> None:
    fixture = GatewayFixture()
    fixture.install(monkeypatch)
    if unsupported == "version":
        fixture.versions = ["2025-03-26"]
    else:
        fixture.capabilities = {"tools": {}, "prompts": {}}
    with pytest.raises(ValueError, match="protocol|capabilities"):
        async with managed_mcp_client(ENDPOINT, Invocation("grant")):
            pytest.fail("Unsupported discovery admitted")
    assert not fixture.calls and all(client.is_closed for client in fixture.clients)


async def test_expired_active_client_cannot_dispatch_later_work(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fixture = GatewayFixture()
    fixture.add("echo", ToolReply({}))
    fixture.block = True
    fixture.install(monkeypatch)
    with pytest.raises(TimeoutError):
        async with managed_mcp_client(ENDPOINT, Invocation("g", time.monotonic() + 0.05)) as client:
            await client.call_tool("echo", {})
    assert len(fixture.calls) == 1 and all(client.is_closed for client in fixture.clients)


async def test_revoked_grant_rejection_is_not_retried(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = GatewayFixture()
    fixture.status = 401
    fixture.install(monkeypatch)
    with pytest.raises(MCPError, match="Server returned an error response"):
        async with managed_mcp_client(ENDPOINT, Invocation("stale")):
            pytest.fail("Revoked grant admitted")
    assert len(fixture.requests) == 1 and not fixture.calls


async def test_slow_client_cleanup_is_bounded(monkeypatch: pytest.MonkeyPatch) -> None:
    fixture = GatewayFixture()
    fixture.block_close = True
    fixture.install(monkeypatch)
    endpoint = McpEndpoint(ENDPOINT.url, 2, 0.02)
    with pytest.raises(TimeoutError):
        async with managed_mcp_client(endpoint, Invocation("grant")):
            pass
    assert all(client.is_closed for client in fixture.clients)
