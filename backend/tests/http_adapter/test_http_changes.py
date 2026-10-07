"""A branch's working copy: append-only changes, pages of changes and their activation."""

import pytest
from slow_thinker_ii.contracts import JsonObject
from support.examples import J1, changed, graph_document

from .http_harness import Api, error, operator_api

SAVED_AT = "2026-10-05T12:00:00.000Z"
CHANGES = "/api/v2/graphs/funny-story/changes"
VERSIONS = "/api/v2/graphs/funny-story/versions"


async def created(api: Api, document: JsonObject | None = None) -> None:
    body = {"document": graph_document(J1) if document is None else document}
    assert (await api.http.post("/api/v2/graphs", json=body)).status_code == 201


def renamed(name: str) -> JsonObject:
    return changed(graph_document(J1), ("name",), name)


def on_main(document: JsonObject) -> JsonObject:
    return {"branch": "main", "document": document}


async def test_a_change_is_recorded_once_per_distinct_document() -> None:
    async with operator_api() as api:
        await created(api)
        first = await api.http.post(CHANGES, json=on_main(renamed("Funnier story")))
        assert (first.status_code, first.json()) == (201, {"change": 2, "at": SAVED_AT})
        same = await api.http.post(CHANGES, json=on_main(renamed("Funnier story")))
        assert (same.status_code, same.json()) == (200, {"change": 2, "at": SAVED_AT})
        draft = changed(graph_document(J1), ("nodes", 1, "component"), "llm-call@9.0.0")
        assert (await api.http.post(CHANGES, json=on_main(draft))).status_code == 201
        moved = changed(graph_document(J1), ("id",), "other-story")
        assert error(await api.http.post(CHANGES, json=on_main(moved))) == (
            422,
            "invalid_document",
        )
        unknown = await api.http.post(
            "/api/v2/graphs/other/changes", json=on_main(renamed("Other"))
        )
        assert error(unknown) == (404, "graph_not_found")
        [summary] = (await api.http.get("/api/v2/graphs")).json()["graphs"]
        assert (summary["latest_change"], summary["active_version"]) == (3, None)


async def test_changes_are_paged_newest_first() -> None:
    async with operator_api() as api:
        await created(api)
        for number in range(2, 5):
            await api.http.post(CHANGES, json=on_main(renamed(f"Story {number}")))
        page = (await api.http.get(CHANGES)).json()["changes"]
        assert [item["change"] for item in page] == [4, 3, 2, 1]
        assert page == [item.to_json() for item in api.platform.library.changes("funny-story")]
        assert set(page[0]) == {"change", "branch", "at", "name", "version"}
        assert (page[0]["name"], page[0]["branch"], page[0]["version"]) == ("Story 4", "main", None)
        older = await api.http.get(CHANGES, params={"before": 3, "limit": 1})
        assert [item["change"] for item in older.json()["changes"]] == [2]
        clamped = await api.http.get(CHANGES, params={"limit": 0})
        assert [item["change"] for item in clamped.json()["changes"]] == [4]
        assert (await api.http.get(CHANGES, params={"before": 0})).json() == {"changes": []}
        missing = await api.http.get("/api/v2/graphs/other/changes")
        assert error(missing) == (404, "graph_not_found")


async def test_a_change_is_read_with_its_document_and_version() -> None:
    async with operator_api() as api:
        await created(api)
        await api.http.post(VERSIONS, json={"change": 1})
        change = (await api.http.get(f"{CHANGES}/1")).json()
        assert change == api.platform.library.change("funny-story", 1).to_json()
        assert set(change) == {"graph_id", "change", "branch", "at", "document", "version"}
        assert (change["document"], change["version"]) == (graph_document(J1), 1)
        listed = (await api.http.get(CHANGES)).json()["changes"]
        assert listed[0]["version"] == 1


@pytest.mark.parametrize(
    "url",
    [
        f"{CHANGES}/2",
        f"{CHANGES}/0",
        f"{CHANGES}/01",
        f"{CHANGES}/one",
        "/api/v2/graphs/x/changes/1",
    ],
)
async def test_unknown_changes_are_not_found(url: str) -> None:
    async with operator_api() as api:
        await created(api)
        assert error(await api.http.get(url)) == (404, "change_not_found")


UNKNOWN_COMPONENT = changed(graph_document(J1), ("nodes", 1, "component"), "llm-call@9.0.0")
MALFORMED: list[JsonObject] = [
    {"change": "1"},
    {"change": 0},
    {"change": True},
    {},
    {"document": {}},
]


async def test_a_change_with_errors_or_a_bad_request_is_not_activated() -> None:
    async with operator_api() as api:
        await created(api, UNKNOWN_COMPONENT)
        refused = await api.http.post(VERSIONS, json={"change": 1})
        assert error(refused) == (422, "invalid_document")
        codes = [item["code"] for item in refused.json()["error"]["diagnostics"]]
        assert "unknown_component" in codes
        for body in ({"change": 2}, {"change": 999_999_999}):
            assert error(await api.http.post(VERSIONS, json=body)) == (404, "change_not_found")
        for body in MALFORMED:
            assert error(await api.http.post(VERSIONS, json=body)) == (422, "invalid_request")
        unknown = await api.http.post("/api/v2/graphs/other/versions", json={"change": 1})
        assert error(unknown) == (404, "change_not_found")


async def test_each_activation_creates_the_next_version_on_the_branch() -> None:
    async with operator_api() as api:
        await created(api, UNKNOWN_COMPONENT)
        fixed = await api.http.post(CHANGES, json=on_main(graph_document(J1)))
        for version in (1, 2):
            activated = await api.http.post(VERSIONS, json={"change": fixed.json()["change"]})
            expected = {"version": version, "branch": "main", "change": 2}
            assert (activated.status_code, activated.json()) == (201, expected)
