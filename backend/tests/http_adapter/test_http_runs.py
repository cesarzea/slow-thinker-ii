"""Runs: admission, summaries, run views, event pages, stops and budget usage."""

import pytest
from slow_thinker_ii.application import RunSettings
from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.contracts import JsonObject
from support.examples import J1, step_one_components

from .http_harness import Api, error, held_call, held_platform, operator_api

STORY = "A cat tried to learn to fly."
START: JsonObject = {"graph_id": "funny-story", "version": 1}


async def started(api: Api, body: JsonObject = START) -> str:
    response = await api.http.post("/api/v2/runs", json=body)
    assert response.status_code == 202
    return response.json()["run_id"]


async def test_a_completed_run_is_listed_read_and_paged() -> None:
    async with operator_api() as api:
        api.platform.saved(J1)
        run_id = await started(api, {**START, "input": "A dog tried to sing."})
        assert (await api.platform.finish(run_id)).status == "completed"
        listed = await api.http.get("/api/v2/runs", params={"graph_id": "funny-story"})
        assert listed.json() == {"runs": [api.platform.runs.runs(None, 1)[0].to_json()]}
        run = await api.http.get(f"/api/v2/runs/{run_id}")
        assert run.json() == api.platform.runs.run(run_id).to_json()
        assert run.json()["results"][0]["name"] == "Funny story"
        url = f"/api/v2/runs/{run_id}/events"
        first = (await api.http.get(url, params={"after": 0, "limit": 2})).json()
        assert ([event["seq"] for event in first["events"]], first["last_seq"]) == ([1, 2], 2)
        assert first["finished"] is False and first["events"][0]["kind"] == "run.started"
        rest = (await api.http.get(url, params={"after": 2})).json()
        assert rest["finished"] is True and rest["events"][-1]["kind"] == "run.finished"
        assert rest == api.platform.runs.events(run_id, 2, 500).to_json()


async def test_an_absent_or_null_input_runs_the_trigger_message() -> None:
    async with operator_api() as api:
        api.platform.saved(J1)
        for body in (START, {**START, "input": None}):
            run_id = await started(api, body)
            [event] = api.platform.run_store.of(run_id, "run.started")
            assert event.data["input"] == STORY
            await api.platform.finish(run_id)


async def test_page_sizes_are_clamped_and_filters_apply() -> None:
    async with operator_api() as api:
        api.platform.saved(J1)
        for _ in range(3):
            await api.platform.finish(await started(api))
        for limit, count in ((0, 1), (2, 2), (1000, 3)):
            listed = await api.http.get("/api/v2/runs", params={"limit": limit})
            assert len(listed.json()["runs"]) == count
        assert len((await api.http.get("/api/v2/runs?graph_id=")).json()["runs"]) == 3
        assert (await api.http.get("/api/v2/runs?graph_id=other")).json() == {"runs": []}
        run_id = (await api.http.get("/api/v2/runs")).json()["runs"][0]["run_id"]
        url = f"/api/v2/runs/{run_id}/events"
        assert len((await api.http.get(url, params={"limit": -5})).json()["events"]) == 1
        everything = len(api.platform.run_store.kinds(run_id))
        assert (
            len((await api.http.get(url, params={"limit": 10**9})).json()["events"]) == everything
        )


@pytest.mark.parametrize(
    ("body", "status", "code"),
    [
        ({"graph_id": "missing", "version": 1}, 404, "graph_not_found"),
        ({"graph_id": "funny-story", "version": 2}, 404, "version_not_found"),
        ({"graph_id": "funny-story"}, 422, "invalid_request"),
        ({"graph_id": "funny-story", "version": "1"}, 422, "invalid_request"),
        ({"graph_id": "funny-story", "version": True}, 422, "invalid_request"),
        ({"graph_id": "funny-story", "version": 0}, 422, "invalid_request"),
        ({"graph_id": "funny-story", "version": 10**9}, 422, "invalid_request"),
        ({"graph_id": 7, "version": 1}, 422, "invalid_request"),
        ({**START, "budget_usd": "1.00"}, 422, "invalid_request"),
        ({**START, "change": 1}, 422, "invalid_request"),
        ({"graph_id": "funny-story", "change": 9}, 404, "change_not_found"),
        ({"graph_id": "funny-story", "change": "1"}, 422, "invalid_request"),
    ],
)
async def test_runs_that_cannot_start(body: JsonObject, status: int, code: str) -> None:
    async with operator_api() as api:
        api.platform.saved(J1)
        assert error(await api.http.post("/api/v2/runs", json=body)) == (status, code)
        assert api.platform.run_store.unfinished() == ()


async def test_a_change_runs_without_a_version() -> None:
    async with operator_api() as api:
        api.platform.saved(J1)
        run_id = await started(api, {"graph_id": "funny-story", "change": 1})
        await api.platform.finish(run_id)
        summary = (await api.http.get(f"/api/v2/runs/{run_id}")).json()
        assert (summary["version"], summary["change"]) == (1, 1)


async def test_a_version_that_no_longer_compiles_is_refused_with_diagnostics() -> None:
    async with operator_api() as api:
        api.platform.saved(J1)
        api.platform.catalog = Catalog(step_one_components(), [])
        response = await api.http.post("/api/v2/runs", json=START)
        assert error(response) == (422, "invalid_document")
        diagnostics = response.json()["error"]["diagnostics"]
        assert [item["code"] for item in diagnostics] == ["unknown_service_entry"]


async def test_the_active_run_limit_is_a_conflict() -> None:
    platform, hosts = held_platform(RunSettings(max_active_runs=1))
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        assert error(await api.http.post("/api/v2/runs", json=START)) == (409, "too_many_runs")
        assert api.platform.run_store.unfinished() == (context.run_id,)


async def test_a_stop_answers_the_current_then_the_final_status() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        url = f"/api/v2/runs/{context.run_id}/stop"
        stopping = await api.http.post(url, json={})
        assert (stopping.status_code, stopping.json()) == (202, {"status": "running"})
        assert (await api.platform.run_store.finished(context.run_id)).status == "cancelled"
        stopped = await api.http.post(url)
        assert (stopped.status_code, stopped.json()) == (202, {"status": "cancelled"})
        assert error(await api.http.post(url, json={"reason": "now"})) == (422, "invalid_request")
        missing = await api.http.post("/api/v2/runs/missing/stop", json={})
        assert error(missing) == (404, "run_not_found")


@pytest.mark.parametrize("url", ["/api/v2/runs/missing", "/api/v2/runs/missing/events"])
async def test_unknown_runs_are_not_found(url: str) -> None:
    async with operator_api() as api:
        assert error(await api.http.get(url)) == (404, "run_not_found")


async def test_usage_reports_the_day_and_month_budgets() -> None:
    async with operator_api() as api:
        response = await api.http.get("/api/v2/usage")
        assert (response.status_code, response.json()) == (200, api.platform.usage.usage())
        assert set(response.json()) == {"day", "month"}
