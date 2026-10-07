"""The catalog and the graph library: validation, creation from drafts, graphs and versions."""

import pytest
from slow_thinker_ii.contracts import JsonValue
from support.examples import J1, changed, graph_document

from .http_harness import error, operator_api

DIAGNOSTIC_FIELDS = {"severity", "code", "message", "path", "node_id"}
UNKNOWN_COMPONENT = ("nodes", 1, "component")  # a draft whose Proposer names no component


async def test_the_catalog_serves_declarations_with_their_origin_and_the_llms() -> None:
    async with operator_api() as api:
        response = await api.http.get("/api/v2/catalog")
        assert response.status_code == 200
        components, llms = response.json()["components"], response.json()["llms"]
        origins = {f"{item['type']}@{item['version']}": item["origin"] for item in components}
        assert origins == {
            "trigger@1.0.0": "platform",
            "output@1.0.0": "platform",
            "llm-call@1.0.0": "package",
            "router@1.0.0": "package",
        }
        declarations = api.platform.catalog.components()
        served = [
            {key: value for key, value in item.items() if key != "origin"} for item in components
        ]
        assert served == [declaration.document for declaration in declarations]
        assert all("origin" not in declaration.document for declaration in declarations)
        assert llms == [entry.document() for entry in api.platform.catalog.llms()]


async def test_validation_returns_diagnostics_and_stores_nothing() -> None:
    async with operator_api() as api:
        valid = await api.http.post(
            "/api/v2/graphs/validate", json={"document": graph_document(J1)}
        )
        assert (valid.status_code, valid.json()) == (200, {"diagnostics": []})
        invalid = await api.http.post("/api/v2/graphs/validate", json={"document": "a story"})
        diagnostics = invalid.json()["diagnostics"]
        assert invalid.status_code == 200
        assert [item["code"] for item in diagnostics] == ["invalid_document"]
        assert set(diagnostics[0]) == DIAGNOSTIC_FIELDS
        assert api.platform.library.graphs() == ()


async def test_a_graph_is_created_once_from_a_draft() -> None:
    async with operator_api() as api:
        draft = changed(graph_document(J1), UNKNOWN_COMPONENT, "llm-call@9.0.0")
        created = await api.http.post("/api/v2/graphs", json={"document": draft})
        assert (created.status_code, created.json()) == (
            201,
            {"id": "funny-story", "branch": "main", "change": 1},
        )
        again = await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})
        assert error(again) == (409, "graph_exists")
        listed = (await api.http.get("/api/v2/graphs")).json()
        assert listed == {"graphs": [item.to_json() for item in api.platform.library.graphs()]}
        [summary] = listed["graphs"]
        assert set(summary) == {"id", "name", "active_version", "latest_change", "updated_at"}
        assert (summary["active_version"], summary["latest_change"]) == (None, 1)
        detail = (await api.http.get("/api/v2/graphs/funny-story")).json()
        assert detail == api.platform.library.graph("funny-story").to_json()
        assert (detail["active_version"], detail["latest_change"], detail["versions"]) == (
            None,
            1,
            [],
        )


@pytest.mark.parametrize(
    "document", ["a story", {"format": "slow-thinker.graph/1", "name": "No identifier"}]
)
async def test_documents_that_are_not_drafts_are_refused(document: JsonValue) -> None:
    async with operator_api() as api:
        response = await api.http.post("/api/v2/graphs", json={"document": document})
        assert error(response) == (422, "invalid_document")
        diagnostics = response.json()["error"]["diagnostics"]
        assert diagnostics and all(set(item) == DIAGNOSTIC_FIELDS for item in diagnostics)
        assert api.platform.library.graphs() == ()


async def test_an_activated_version_is_listed_and_read_with_its_change() -> None:
    async with operator_api() as api:
        await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})
        url = "/api/v2/graphs/funny-story/versions"
        activated = await api.http.post(url, json={"change": 1})
        expected = {"version": 1, "branch": "main", "change": 1}
        assert (activated.status_code, activated.json()) == (201, expected)
        version = (await api.http.get(f"{url}/1")).json()
        assert version == api.platform.library.version("funny-story", 1).to_json()
        assert set(version) == {
            "graph_id",
            "version",
            "branch",
            "parent",
            "change",
            "created_at",
            "document",
        }
        assert (version["change"], version["document"]) == (1, graph_document(J1))
        detail = (await api.http.get("/api/v2/graphs/funny-story")).json()
        assert (detail["active_version"], detail["latest_change"]) == (1, 1)
        [listed] = detail["versions"]
        assert set(listed) == {"version", "branch", "parent", "change", "name", "created_at"}
        assert (listed["version"], listed["parent"], listed["name"]) == (1, None, "Funny story")


@pytest.mark.parametrize(
    ("url", "code"),
    [
        ("/api/v2/graphs/missing", "graph_not_found"),
        ("/api/v2/graphs/missing/versions/1", "version_not_found"),
        ("/api/v2/graphs/funny-story/versions/2", "version_not_found"),
        ("/api/v2/graphs/funny-story/versions/0", "version_not_found"),
        ("/api/v2/graphs/funny-story/versions/01", "version_not_found"),
        ("/api/v2/graphs/funny-story/versions/one", "version_not_found"),
    ],
)
async def test_unknown_graphs_and_versions_are_not_found(url: str, code: str) -> None:
    async with operator_api() as api:
        await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})
        await api.http.post("/api/v2/graphs/funny-story/versions", json={"change": 1})
        assert error(await api.http.get(url)) == (404, code)
