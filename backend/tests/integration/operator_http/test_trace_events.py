"""Event inspection is bounded, stable, run-scoped and unable to dispatch work."""

import pytest
from support.operator_http import HttpCase, payload
from support.operator_trace import completed_trace, event_items, objects


async def test_event_pages_freeze_sequence_while_new_evidence_arrives(api: HttpCase) -> None:
    run, _ = await completed_trace(api)
    path = f"/api/v1/runs/{run}/events"
    first = payload(await api.client.get(path))
    upper, cursor = first["through_sequence"], first["next_cursor"]
    assert isinstance(upper, int) and isinstance(cursor, str)
    with api.case.runs.begin() as transaction:
        transaction.event(run, "evidence.gap", None, '{"reason":"fixture"}')
    items = objects(first["items"])
    while cursor is not None:
        page = payload(await api.client.get(path, params={"cursor": cursor}))
        assert page["through_sequence"] == upper
        items.extend(objects(page["items"]))
        cursor = page["next_cursor"]
        assert cursor is None or isinstance(cursor, str)
    assert [item["sequence"] for item in items] == list(range(1, upper + 1))
    assert len(await event_items(api, run)) == upper + 1
    assert len(api.case.preparer.operation.calls) == 1


async def test_event_cursors_are_not_transferable_to_other_queries_or_runs(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    first = payload(await api.client.get(f"/api/v1/runs/{run}/events"))
    cursor = first["next_cursor"]
    assert isinstance(cursor, str)
    other, _ = await completed_trace(api, "another")
    for path in (f"/runs/{other}/events", f"/runs/{run}/calls/{call}", "/workspace"):
        response = await api.client.get("/api/v1" + path, params={"cursor": cursor})
        assert response.status_code == 400


@pytest.mark.parametrize("query", ["cursor=bad", "cursor=a&cursor=b", "limit=999999"])
async def test_invalid_event_paging_fails_explicitly(api: HttpCase, query: str) -> None:
    run, _ = await completed_trace(api)
    response = await api.client.get(f"/api/v1/runs/{run}/events?{query}")
    assert response.status_code == 400


async def test_metadata_pages_reference_retained_payload_and_support_cache_validation(
    api: HttpCase,
) -> None:
    run, _ = await completed_trace(api)
    url = f"/api/v1/runs/{run}/events"
    response = await api.client.get(url)
    first = objects(payload(response)["items"])[0]
    assert first["event"] == "run.created" and "payload_json" not in first
    assert isinstance(first["received_at"], str)
    content = payload(await api.client.get(f"/api/v1/runs/{run}/payloads/{first['payload_id']}"))
    assert content["status"] == "present" and isinstance(content["content"], dict)
    assert (
        await api.client.get(url, headers={"if-none-match": response.headers["etag"]})
    ).status_code == 304
    assert (await api.client.get("/api/v1/runs/missing/events")).status_code == 404
