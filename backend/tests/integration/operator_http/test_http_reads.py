"""Read views use complete cache versions, stable paging and read-only storage access."""

from dataclasses import replace

import pytest
from slow_thinker_ii.contracts import json_object
from support.coordinator import eventually
from support.operator_http import HttpCase, payload


async def test_workspace_etag_covers_policy_changes(api: HttpCase) -> None:
    first = await api.client.get("/api/v1/workspace")
    assert first.status_code == 200 and payload(first)["admission_available"] is True
    etag = first.headers["etag"]
    assert etag == '"' + str(payload(first)["view_token"]) + '"'
    assert (
        await api.client.get("/api/v1/workspace", headers={"if-none-match": etag})
    ).status_code == 304
    profile = api.case.base.profile
    api.case.commands.configure(
        replace(profile, revision="next", limits=replace(profile.limits, month_budget=20000))
    )
    changed = await api.client.get("/api/v1/workspace", headers={"if-none-match": etag})
    assert changed.status_code == 200 and changed.headers["etag"] != etag
    assert json_object(payload(changed)["month_budget"])["cap"] == "0.000020000"


async def test_run_etag_covers_shared_cost_without_run_event(api: HttpCase) -> None:
    identity = payload(await api.client.post("/api/v1/runs", json=api.start()))["target_id"]
    await eventually(lambda: not api.case.coordinator.pending().runs)
    url = f"/api/v1/runs/{identity}"
    first = await api.client.get(url)
    with api.case.base.database.transaction() as db:
        db.execute("UPDATE budget_scopes SET settled=1 WHERE kind='session'")
    second = await api.client.get(url, headers={"if-none-match": first.headers["etag"]})
    assert second.status_code == 200 and second.headers["etag"] != first.headers["etag"]
    assert payload(second)["last_event_sequence"] == payload(first)["last_event_sequence"]
    assert json_object(payload(second)["session_budget"])["settled"] == "0.000000001"


async def test_session_pages_exclude_later_insertions(api: HttpCase) -> None:
    for number in range(2):
        api.case.commands.create_session(f"s{number}", f"Session {number}")
    first = json_object(payload(await api.client.get("/api/v1/workspace"))["sessions"])
    items = first["items"]
    assert isinstance(items, list) and len(items) == 2
    cursor = first["next_cursor"]
    assert isinstance(cursor, str)
    api.case.commands.create_session("later", "Later")
    second = json_object(
        payload(await api.client.get("/api/v1/workspace", params={"cursor": cursor}))["sessions"]
    )
    items = second["items"]
    assert isinstance(items, list) and len(items) == 1
    assert json_object(items[0])["name"] == "Session 1"
    assert second["next_cursor"] is None
    foreign = await api.client.get(
        f"/api/v1/sessions/{api.case.base.session_id}/runs", params={"cursor": cursor}
    )
    assert foreign.status_code == 400


@pytest.mark.parametrize("cursor", ["broken", "x.y", "x.ñ", "a" * 1025])
async def test_invalid_page_cursor(api: HttpCase, cursor: str) -> None:
    response = await api.client.get("/api/v1/workspace", params={"cursor": cursor})
    assert response.status_code == 400


async def test_history_is_scoped_to_saved_session(api: HttpCase) -> None:
    for number in range(3):
        assert (
            await api.client.post("/api/v1/runs", json=api.start(f"start{number}"))
        ).status_code == 202
        await eventually(lambda: not api.case.coordinator.pending().runs)
    url = f"/api/v1/sessions/{api.case.base.session_id}/runs"
    first = payload(await api.client.get(url))
    cursor = first["next_cursor"]
    assert isinstance(cursor, str)
    second = payload(await api.client.get(url, params={"cursor": cursor}))
    items = second["items"]
    assert isinstance(items, list) and len(items) == 1
    assert json_object(items[0])["session_id"] == api.case.base.session_id
    empty = api.case.commands.create_session("empty", "Empty").receipt.target_id
    assert payload(await api.client.get(f"/api/v1/sessions/{empty}/runs"))["items"] == []


async def test_workspace_inspection_does_not_cache_cleanup(api: HttpCase) -> None:
    await api.client.post("/api/v1/runs", json=api.start())
    await eventually(lambda: not api.case.coordinator.pending().runs)
    for _ in range(2):
        assert payload(await api.client.get("/api/v1/workspace"))["admission_available"] is True
    with api.case.base.database.transaction() as db:
        assert db.execute("SELECT cleanup_confirmed FROM operator_runs").fetchone()[0] == 0


async def test_duplicate_query_parameters_rejected(api: HttpCase) -> None:
    response = await api.client.get("/api/v1/workspace?cursor=a&cursor=b")
    assert response.status_code == 400
