"""Trace fixtures follow public operator reads and retain real coordinator records."""

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object

from .coordinator import eventually
from .operator_http import HttpCase, payload


async def completed_trace(api: HttpCase, command: str = "start") -> tuple[str, str]:
    receipt = payload(await api.client.post("/api/v1/runs", json=api.start(command)))
    run = str(receipt["target_id"])
    await eventually(lambda: not api.case.coordinator.pending().runs)
    events = await event_items(api, run)
    call = next(item["call_id"] for item in events if item["event"] == "call.requested")
    assert isinstance(call, str)
    return run, call


async def event_items(api: HttpCase, run: str) -> list[JsonObject]:
    cursor: str | None = None
    result: list[JsonObject] = []
    while True:
        params = {} if cursor is None else {"cursor": cursor}
        response = await api.client.get(f"/api/v1/runs/{run}/events", params=params)
        assert response.status_code == 200
        page = payload(response)
        result.extend(objects(page["items"]))
        next_cursor = page["next_cursor"]
        assert next_cursor is None or isinstance(next_cursor, str)
        cursor = next_cursor
        if cursor is None:
            return result


def objects(value: JsonValue) -> list[JsonObject]:
    assert isinstance(value, list)
    return [json_object(item) for item in value]
