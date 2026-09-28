"""Inspection evidence comes from actual installed component calls through HTTP."""

from decimal import Decimal

import httpx
from slow_thinker_ii.contracts import JsonObject, json_object
from support.operator_http import payload
from support.operator_trace import objects

from .activation_checks import inspect_activations


async def inspect_trace(client: httpx.AsyncClient, run: str, count: int, *, stop: bool) -> None:
    base = f"/api/v1/runs/{run}"
    events = await read_events(client, base)
    ids = {str(event["call_id"]) for event in events if event["event"] == "call.requested"}
    calls = [payload(await client.get(f"{base}/calls/{call}")) for call in ids]
    children = [
        call for call in calls if json_object(call["context"])["parent_call_id"] is not None
    ]
    assert children and all(
        json_object(call["context"])["parent_call_id"] in ids for call in children
    )
    charged = [json_object(call["accounting"]) for call in calls if call["accounting"] is not None]
    if stop:
        assert any(Decimal(str(item["outstanding"])) > 0 for item in charged)
    else:
        assert len(charged) == count
        assert (
            sum(Decimal(str(item["amount"])) for item in charged) == Decimal("0.000002390") * count
        )
        assert all(json_object(call["context"])["node_id"] is not None for call in children)
    for call in calls:
        await inspect_payloads(client, base, call)
    await inspect_activations(client, base, calls)


async def read_events(client: httpx.AsyncClient, base: str) -> list[JsonObject]:
    items: list[JsonObject] = []
    cursor: str | None = None
    while True:
        response = await client.get(
            base + "/events", params={} if cursor is None else {"cursor": cursor}
        )
        assert response.status_code == 200
        page = payload(response)
        items.extend(objects(page["items"]))
        next_cursor = page["next_cursor"]
        assert next_cursor is None or isinstance(next_cursor, str)
        cursor = next_cursor
        if cursor is None:
            return items


async def inspect_payloads(client: httpx.AsyncClient, base: str, call: JsonObject) -> None:
    request = await client.get(f"{base}/payloads/{call['request_payload_id']}")
    assert request.status_code == 200 and payload(request)["status"] == "present"
    assert "synthetic-preparation-key" not in request.text
    for receipt in objects(json_object(call["receipts"])["items"]):
        response = await client.get(f"{base}/payloads/{receipt['response_payload_id']}")
        assert response.status_code == 200 and payload(response)["status"] == "present"
        assert "synthetic-preparation-key" not in response.text
