"""Branches: `main` from creation, branches from a version or a change, changes per branch."""

import pytest
from slow_thinker_ii.contracts import JsonObject, JsonValue
from support.examples import J1, changed, graph_document

from .http_harness import Api, error, operator_api

GRAPH = "/api/v2/graphs/funny-story"
SAVED_AT = "2026-10-05T12:00:00.000Z"


async def prepared(api: Api) -> None:
    """J1 with version 1 activated from change 1, and the branch `Shorter` from version 1."""
    assert (await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})).is_success
    assert (await api.http.post(f"{GRAPH}/versions", json={"change": 1})).is_success
    started = await api.http.post(
        f"{GRAPH}/branches", json={"name": "Shorter", "from": {"version": 1}}
    )
    assert (started.status_code, started.json()) == (201, {"name": "Shorter", "change": 2})


def renamed(name: str) -> JsonObject:
    return changed(graph_document(J1), ("name",), name)


async def test_branches_are_listed_oldest_first_with_their_start() -> None:
    async with operator_api() as api:
        await prepared(api)
        wilder = await api.http.post(
            f"{GRAPH}/branches", json={"name": "Wilder ideas", "from": {"change": 1}}
        )
        assert (wilder.status_code, wilder.json()) == (201, {"name": "Wilder ideas", "change": 3})
        branches = (await api.http.get(f"{GRAPH}/branches")).json()["branches"]
        expected = [item.to_json() for item in api.platform.library.branches("funny-story")]
        assert branches == expected
        assert [item["name"] for item in branches] == ["main", "Shorter", "Wilder ideas"]
        main, shorter, _ = branches
        assert main == {
            "name": "main",
            "created_at": SAVED_AT,
            "from_version": None,
            "from_change": None,
            "latest_change": 1,
            "head_version": 1,
        }
        assert (shorter["from_version"], shorter["latest_change"]) == (1, 2)
        assert (await api.http.get(GRAPH)).json()["branches"] == branches
        first = (await api.http.get(f"{GRAPH}/changes/2")).json()
        assert (first["branch"], first["document"]) == ("Shorter", graph_document(J1))
        missing = await api.http.get("/api/v2/graphs/other/branches")
        assert error(missing) == (404, "graph_not_found")


async def test_changes_are_recorded_and_listed_per_branch() -> None:
    async with operator_api() as api:
        await prepared(api)
        body = {"branch": "Shorter", "document": renamed("Short story")}
        recorded = await api.http.post(f"{GRAPH}/changes", json=body)
        assert (recorded.status_code, recorded.json()) == (201, {"change": 3, "at": SAVED_AT})
        same = await api.http.post(f"{GRAPH}/changes", json=body)
        assert (same.status_code, same.json()["change"]) == (200, 3)
        for query, numbers in (("?branch=Shorter", [3, 2]), ("?branch=main", [1]), ("", [3, 2, 1])):
            page = (await api.http.get(f"{GRAPH}/changes{query}")).json()["changes"]
            assert [item["change"] for item in page] == numbers
        assert len((await api.http.get(f"{GRAPH}/changes?branch=")).json()["changes"]) == 3
        unknown = {"branch": "Longer", "document": renamed("Long story")}
        assert error(await api.http.post(f"{GRAPH}/changes", json=unknown)) == (
            404,
            "branch_not_found",
        )
        listed = await api.http.get(f"{GRAPH}/changes?branch=Longer")
        assert error(listed) == (404, "branch_not_found")
        for wrong in ({"document": renamed("x")}, {"branch": 1, "document": renamed("x")}):
            refused = await api.http.post(f"{GRAPH}/changes", json=wrong)
            assert error(refused) == (422, "invalid_request")


async def test_activation_follows_the_branch_lineage() -> None:
    async with operator_api() as api:
        await prepared(api)
        activated = await api.http.post(f"{GRAPH}/versions", json={"change": 2})
        expected = {"version": 2, "branch": "Shorter", "change": 2}
        assert (activated.status_code, activated.json()) == (201, expected)
        version = (await api.http.get(f"{GRAPH}/versions/2")).json()
        assert (version["branch"], version["parent"], version["change"]) == ("Shorter", 1, 2)
        detail = (await api.http.get(GRAPH)).json()
        assert detail["active_version"] == 2
        assert [(item["version"], item["parent"]) for item in detail["versions"]] == [
            (1, None),
            (2, 1),
        ]


@pytest.mark.parametrize(
    ("body", "status", "code"),
    [
        ({"name": "shorter", "from": {"version": 1}}, 409, "branch_exists"),
        ({"name": "MAIN", "from": {"change": 1}}, 409, "branch_exists"),
        ({"name": "", "from": {"version": 1}}, 422, "invalid_request"),
        ({"name": "-draft", "from": {"version": 1}}, 422, "invalid_request"),
        ({"name": "a/b", "from": {"version": 1}}, 422, "invalid_request"),
        ({"name": "x" * 41, "from": {"version": 1}}, 422, "invalid_request"),
        ({"name": 7, "from": {"version": 1}}, 422, "invalid_request"),
        ({"name": "Next", "from": {"version": 9}}, 404, "version_not_found"),
        ({"name": "Next", "from": {"change": 9}}, 404, "change_not_found"),
        ({"name": "Next", "from": {}}, 422, "invalid_request"),
        ({"name": "Next", "from": {"version": 1, "change": 1}}, 422, "invalid_request"),
        ({"name": "Next", "from": {"branch": "main"}}, 422, "invalid_request"),
        ({"name": "Next", "from": {"version": "1"}}, 422, "invalid_request"),
        ({"name": "Next", "from": "main"}, 422, "invalid_request"),
        ({"name": "Next"}, 422, "invalid_request"),
        ({"name": "Next", "from": {"version": 1}, "document": {}}, 422, "invalid_request"),
    ],
)
async def test_branches_that_cannot_start(
    body: dict[str, JsonValue], status: int, code: str
) -> None:
    async with operator_api() as api:
        await prepared(api)
        assert error(await api.http.post(f"{GRAPH}/branches", json=body)) == (status, code)
        assert len(api.platform.library.branches("funny-story")) == 2
