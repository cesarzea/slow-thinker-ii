"""Authenticated native denials and MCP transport refusals never reach business operations."""

from pathlib import Path

import httpx
import pytest
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import mcp_router
from slow_thinker_ii.application import ModelBinding, NativeModelGateway
from slow_thinker_ii.contracts import JsonObject, encode_json
from support.authority import MODEL, PROPOSER
from support.mcp_gateway import McpCase, mcp_case
from support.native_server import gateway_app


@pytest.mark.parametrize(
    "mode,reason",
    [
        ("missing", "model_alias_required"),
        ("unbound", "model_binding_denied"),
        ("forbidden", "model_operation_denied"),
    ],
)
async def test_native_denial_is_durable_and_parent_scoped(
    tmp_path: Path, mode: str, reason: str
) -> None:
    case = mcp_case(tmp_path)
    target = PROPOSER if mode == "forbidden" else MODEL
    gateway = NativeModelGateway(
        case.native.run.authority,
        case.native.calls,
        (ModelBinding("proposer", "bound-model", target),),
        case.service,
    )
    body: JsonObject = (
        {} if mode == "missing" else {"model": "unknown" if mode == "unbound" else "bound-model"}
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/v1/chat/completions",
            content=encode_json(body),
            headers={
                "authorization": f"Bearer {case.native.parent.token}",
                "content-type": "application/json",
            },
        )
    assert reply.status_code == (400 if mode == "missing" else 403)
    assert not case.native.model.calls
    assert_denial(case, reason)


@pytest.mark.parametrize(
    "mode,status",
    [("missing", 401), ("revoked", 403), ("origin", 403), ("version", 400), ("body", 413)],
)
async def test_mcp_http_guards_prevent_dispatch(tmp_path: Path, mode: str, status: int) -> None:
    case = mcp_case(tmp_path)
    app = FastAPI()
    app.include_router(mcp_router(case.service, 32 if mode == "body" else 1024))
    headers = {
        "authorization": f"Bearer {case.native.parent.token}",
        "content-type": "application/json",
        "accept": "application/json, text/event-stream",
        "mcp-protocol-version": "2026-07-28",
    }
    if mode == "missing":
        del headers["authorization"]
    elif mode == "revoked":
        case.native.run.authority.revoke(case.native.parent.context.call_id)
    elif mode == "origin":
        headers["origin"] = "https://untrusted.invalid"
    elif mode == "version":
        headers["mcp-protocol-version"] = "1999-01-01"
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/mcp",
            headers=headers,
            content=encode_json({"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}),
        )
    assert reply.status_code == status and not case.native.model.calls


def assert_denial(case: McpCase, reason: str) -> None:
    with case.native.run.store.begin() as transaction:
        denials = [event for event in transaction.events("run") if event.event == "call.rejected"]
    assert len(denials) == 1 and reason in denials[0].payload_json
    assert denials[0].call_id == case.native.parent.context.call_id
