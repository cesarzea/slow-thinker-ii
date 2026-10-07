"""Operator bodies are bounded JSON objects with known fields; queries and errors are strict."""

from collections.abc import AsyncIterator

import pytest
from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.contracts import JsonValue
from support.examples import J1, graph_document
from support.platform import Platform

from .http_harness import error, http_settings, operator_api, services

JSON = {"content-type": "application/json"}


@pytest.mark.parametrize(
    ("content", "status", "code"),
    [
        (b'{"document": {}, "document": {}}', 400, "invalid_json"),
        (b'{"document": NaN}', 400, "invalid_json"),
        (b"{", 400, "invalid_json"),
        (b"\xff", 400, "invalid_json"),
        (b"[" * 100_000, 400, "invalid_json"),
        (b"[]", 422, "invalid_request"),
        (b'{"document": {}, "snapshot": "forged"}', 422, "invalid_request"),
        (b"{}", 422, "invalid_request"),
        (b"", 422, "invalid_request"),
    ],
)
async def test_invalid_bodies_store_nothing(content: bytes, status: int, code: str) -> None:
    async with operator_api() as api:
        response = await api.http.post("/api/v2/graphs", content=content, headers=JSON)
        assert error(response) == (status, code)
        assert api.platform.library.graphs() == ()


@pytest.mark.parametrize(
    "headers",
    [{"content-type": "text/plain"}, {}, {**JSON, "content-encoding": "gzip"}],
)
async def test_bodies_are_uncompressed_json(headers: dict[str, str]) -> None:
    async with operator_api() as api:
        response = await api.http.post(
            "/api/v2/graphs/validate", content=b'{"document": {}}', headers=headers
        )
        assert error(response) == (415, "json_content_required")


async def test_bodies_beyond_the_bound_are_refused_before_parsing() -> None:
    async with operator_api(settings=http_settings(limit=64)) as api:
        declared = await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})
        assert error(declared) == (413, "request_too_large")
        streamed = await api.http.post("/api/v2/graphs", content=chunks(b" " * 65), headers=JSON)
        assert error(streamed) == (413, "request_too_large")
        for length in ("0000000000000000000065", "9" * 40):
            headers = {**JSON, "content-length": length}
            response = await api.http.post("/api/v2/graphs", content=b"{}", headers=headers)
            assert error(response) == (413, "request_too_large")
        assert api.platform.library.graphs() == ()
        within = await api.http.post("/api/v2/runs/r/stop", content=chunks(b"{}"), headers=JSON)
        assert error(within) == (404, "run_not_found")


async def chunks(content: bytes) -> AsyncIterator[bytes]:
    for start in range(0, len(content), 16):
        yield content[start : start + 16]


@pytest.mark.parametrize(
    "url",
    [
        "/api/v2/graphs?expand=1",
        "/api/v2/catalog?x=",
        "/api/v2/runs?limit=ten",
        "/api/v2/runs?limit=",
        "/api/v2/runs?limit=1&limit=2",
        "/api/v2/runs/r/events?after=-1",
        "/api/v2/runs/r/events?after=1.5",
        "/api/v2/runs/r?verbose=1",
        "/api/v2/usage?verbose=true",
        "/api/v2/graphs/g/changes?before=-1",
        "/api/v2/graphs/g/changes?before=",
        "/api/v2/graphs/g/changes?limit=many",
        "/api/v2/graphs/g/changes?before=1&before=2",
        "/api/v2/graphs/g/changes?branch=a&branch=b",
        "/api/v2/graphs/g/branches?name=main",
        "/api/v2/graphs/g/changes?cursor=1",
        "/api/v2/graphs/g/changes/1?verbose=1",
    ],
)
async def test_unknown_or_malformed_query_parameters_are_refused(url: str) -> None:
    async with operator_api() as api:
        assert error(await api.http.get(url)) == (422, "invalid_query")


@pytest.mark.parametrize(
    ("url", "body"),
    [
        ("/api/v2/graphs/validate?dry=1", {"document": {}}),
        ("/api/v2/graphs/g/changes?dry=1", {"document": {}}),
        ("/api/v2/graphs/g/versions?dry=1", {"change": 1}),
        ("/api/v2/graphs/g/branches?dry=1", {"name": "b", "from": {"change": 1}}),
    ],
)
async def test_commands_take_no_query_parameters(url: str, body: dict[str, JsonValue]) -> None:
    async with operator_api() as api:
        assert error(await api.http.post(url, json=body)) == (422, "invalid_query")


async def test_error_messages_stay_within_the_interface_bound() -> None:
    async with operator_api() as api:
        response = await api.http.get("/api/v2/runs/" + "r" * 3000)
        message = response.json()["error"]["message"]
        assert error(response) == (404, "run_not_found")
        assert len(message) == 2000 and message.endswith("…")


async def test_unexpected_failures_answer_a_bounded_error() -> None:
    def broken() -> Catalog:
        raise OSError("/Users/someone/state.sqlite3 is locked")

    platform = Platform()
    replaced = services(platform, broken)
    async with operator_api(platform, http_services=replaced, raise_errors=False) as api:
        response = await api.http.get("/api/v2/catalog")
        assert response.status_code == 500
        message = "The server could not complete the request."
        assert response.json() == {"error": {"code": "internal_error", "message": message}}
        assert response.headers["cache-control"] == "no-store"
        assert "/Users/" not in response.text
