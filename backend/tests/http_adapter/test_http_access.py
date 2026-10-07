"""Operator requests need the token, one exact host and an allowed origin; no reply is cached."""

import pytest
from support.examples import J1, graph_document

from .http_harness import HOST, ORIGIN, TOKEN, error, operator_api


@pytest.mark.parametrize(
    ("header", "value", "status", "code"),
    [
        ("authorization", "Bearer wrong", 401, "operator_authentication_required"),
        ("authorization", "", 401, "operator_authentication_required"),
        ("authorization", TOKEN, 401, "operator_authentication_required"),
        ("host", "evil.example", 403, "operator_host_denied"),
        ("host", "127.0.0.1:9000", 403, "operator_host_denied"),
        ("origin", "http://evil.example", 403, "operator_origin_denied"),
        ("origin", "null", 403, "operator_origin_denied"),
        ("sec-fetch-site", "cross-site", 403, "operator_origin_denied"),
    ],
)
async def test_untrusted_requests_reach_no_use_case(
    header: str, value: str, status: int, code: str
) -> None:
    async with operator_api() as api:
        body = {"document": graph_document(J1)}
        response = await api.http.post("/api/v2/graphs", json=body, headers={header: value})
        assert error(response) == (status, code)
        assert response.headers["cache-control"] == "no-store"
        assert TOKEN not in response.text
        assert api.platform.library.graphs() == ()


@pytest.mark.parametrize("header", ["authorization", "origin", "host"])
async def test_repeated_security_headers_are_refused(header: str) -> None:
    value = {"authorization": f"Bearer {TOKEN}", "origin": ORIGIN, "host": HOST}[header]
    async with operator_api() as api:
        response = await api.http.get("/api/v2/usage", headers=[(header, value), (header, value)])
        assert response.status_code in (401, 403)


async def test_allowed_hosts_and_origins_are_served_without_caching() -> None:
    async with operator_api() as api:
        browser = {"origin": ORIGIN, "sec-fetch-site": "same-site"}
        for headers in ({}, browser, {"host": "localhost:8000"}):
            response = await api.http.get("/api/v2/usage", headers=headers)
            assert response.status_code == 200
            assert response.headers["cache-control"] == "no-store"


async def test_unknown_operator_resources_are_guarded_then_not_found() -> None:
    async with operator_api() as api:
        anonymous = await api.http.get("/api/v2/secrets", headers={"authorization": ""})
        assert error(anonymous) == (401, "operator_authentication_required")
        unknown = [("GET", "/api/v2/secrets"), ("DELETE", "/api/v2/graphs")]
        for method, path in [*unknown, ("TRACE", "/api/v2/usage"), ("PURGE", "/api/v2/runs")]:
            response = await api.http.request(method, path)
            assert error(response) == (404, "not_found")
            assert response.headers["cache-control"] == "no-store"
        assert error(await api.http.get("/api/v2")) == (404, "not_found")


async def test_other_paths_are_not_operator_resources() -> None:
    async with operator_api() as api:
        response = await api.http.get("/api/v20/graphs", headers={"authorization": ""})
        assert response.status_code == 404
        assert "cache-control" not in response.headers
        assert (await api.http.get("/docs")).status_code == 404
        assert (await api.http.get("/openapi.json")).status_code == 404
