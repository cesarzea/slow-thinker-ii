"""Installed workflows are controlled and observed through the actual authenticated application."""

import asyncio
from decimal import Decimal
from pathlib import Path

import httpx
import pytest
from slow_thinker_ii.accounting import display_amount
from slow_thinker_ii.contracts import JsonObject, json_object
from support.native_server import serve
from support.operator_http import payload
from support.sequence_plans import graph_value
from support.upstream import Upstream

from .conftest import PreparedBundle
from .operator_fixture import operator_application
from .trace_checks import inspect_trace


@pytest.mark.parametrize(
    "name,stop",
    [
        ("single-agent", False),
        ("handoff", False),
        ("review-cycle", False),
        ("repeated-review", False),
        ("single-agent", True),
    ],
)
async def test_operator_application(
    tmp_path: Path, prepared_bundle: PreparedBundle, name: str, stop: bool
) -> None:
    upstream = Upstream(blocked=stop)
    async with (
        serve(upstream.app) as provider,
        operator_application(tmp_path, prepared_bundle, name, provider) as (client, count),
    ):
        intent = await start_body(client, name)
        started = await client.post("/api/v1/runs", json=intent)
        assert started.status_code == 202, started.text
        identity = str(payload(started)["target_id"])
        assert payload(await client.post("/api/v1/runs", json=intent))["replayed"] is True
        if stop:
            await asyncio.wait_for(upstream.entered.wait(), 40)
            reply = await client.post(
                f"/api/v1/runs/{identity}/stop",
                json={"schema_version": "0.1-draft", "command_id": "stop"},
            )
            assert reply.status_code == 202
        result = await finished(client, identity)
        upstream.release.set()
        assert_result(result, count, stop=stop)
        snapshot = await client.get(f"/api/v1/runs/{identity}/definition")
        assert snapshot.status_code == 200 and "synthetic-preparation-key" not in snapshot.text
        assert '"tariff"' in snapshot.text and '"installations"' in snapshot.text
        await inspect_trace(client, identity, count, stop=stop)
    assert len(upstream.requests) == (1 if stop else count)


async def start_body(client: httpx.AsyncClient, name: str) -> JsonObject:
    session = payload(
        await client.post(
            "/api/v1/sessions",
            json={"schema_version": "0.1-draft", "command_id": "session", "name": "Installed HTTP"},
        )
    )
    workspace = payload(await client.get("/api/v1/workspace"))
    graph = graph_value(name)
    return {
        "schema_version": "0.1-draft",
        "command_id": "start",
        "session_id": session["target_id"],
        "graph_id": graph["graph_id"],
        "graph_revision": graph["revision"],
        "configuration_revision": workspace["configuration_revision"],
        "input": {"problem": "Design a workshop"},
    }


async def finished(client: httpx.AsyncClient, identity: str) -> JsonObject:
    async with asyncio.timeout(80):
        while True:
            result = payload(await client.get(f"/api/v1/runs/{identity}"))
            if (
                result["state"] not in ("created", "running", "stopping")
                and result["cleanup"] == "confirmed"
            ):
                return result
            await asyncio.sleep(0.05)


def assert_result(result: JsonObject, count: int, *, stop: bool) -> None:
    assert result["state"] == ("cancelled" if stop else "completed")
    scopes = [
        json_object(result[key]) for key in ("budget", "session_budget", "admission_month_budget")
    ]
    if stop:
        assert all(Decimal(str(scope["outstanding"])) > 0 for scope in scopes)
    else:
        assert all(scope["settled"] == display_amount(2390 * count) for scope in scopes)
        assert all(scope["outstanding"] == display_amount(0) for scope in scopes)
