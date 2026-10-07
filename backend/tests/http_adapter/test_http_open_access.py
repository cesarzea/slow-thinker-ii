"""Without an operator token nothing but the bearer check changes; `GET /access` is public."""

import pytest
from support.examples import J1, LUNA, graph_document

from .http_harness import ORIGIN, TOKEN, error, http_settings, operator_api
from .http_mcp import raw_call, raw_headers

OPEN = http_settings(token=None)
BROWSER = {"origin": ORIGIN, "sec-fetch-site": "same-origin"}
ONLY_THIS_MACHINE = "Requests without an operator token are accepted only from this machine."


async def test_without_a_token_operator_requests_need_no_authorization() -> None:
    async with operator_api(settings=OPEN, authorized=False) as api:
        created = await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})
        assert created.status_code == 201
        assert created.headers["cache-control"] == "no-store"
        stale = await api.http.get("/api/v2/graphs", headers={"authorization": "Bearer stale"})
        assert stale.status_code == 200 and len(stale.json()["graphs"]) == 1
        assert (await api.http.get("/api/v2/usage", headers=BROWSER)).status_code == 200
        assert error(await api.http.get("/api/v2/secrets")) == (404, "not_found")


@pytest.mark.parametrize(
    ("header", "value", "code"),
    [
        ("host", "evil.example", "operator_host_denied"),
        ("host", "127.0.0.1:9000", "operator_host_denied"),
        ("origin", "http://evil.example", "operator_origin_denied"),
        ("origin", "null", "operator_origin_denied"),
        ("sec-fetch-site", "cross-site", "operator_origin_denied"),
    ],
)
@pytest.mark.parametrize("token", [None, TOKEN])
async def test_host_and_origin_refusals_hold_in_both_modes(
    token: str | None, header: str, value: str, code: str
) -> None:
    async with operator_api(settings=http_settings(token=token), authorized=False) as api:
        for path in ("/api/v2/usage", "/api/v2/access"):
            response = await api.http.get(path, headers={header: value})
            assert error(response) == (403, code)
            assert response.headers["cache-control"] == "no-store"
        assert api.platform.library.graphs() == ()


@pytest.mark.parametrize("peer", ["127.0.0.1", "127.8.9.10", "::1", "::ffff:127.0.0.1"])
async def test_without_a_token_this_machine_is_served(peer: str) -> None:
    async with operator_api(settings=OPEN, authorized=False, peer=peer) as api:
        for path in ("/api/v2/usage", "/api/v2/access"):
            assert (await api.http.get(path)).status_code == 200


@pytest.mark.parametrize("peer", ["10.0.0.7", "192.168.1.20", "2001:db8::1", "testclient", None])
async def test_without_a_token_other_peers_are_refused(peer: str | None) -> None:
    async with operator_api(settings=OPEN, authorized=False, peer=peer) as api:
        for path in ("/api/v2/usage", "/api/v2/access"):
            response = await api.http.get(path)
            assert error(response) == (403, "operator_client_denied")
            assert response.json()["error"]["message"] == ONLY_THIS_MACHINE
            assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("peer", ["10.0.0.7", None])
async def test_with_a_token_the_peer_is_not_checked(peer: str | None) -> None:
    async with operator_api(peer=peer) as api:
        assert (await api.http.get("/api/v2/usage")).status_code == 200
        access = await api.http.get("/api/v2/access", headers={"authorization": ""})
        assert access.json() == {"authentication": "token"}


async def test_without_a_token_bodies_stay_bounded() -> None:
    async with operator_api(settings=http_settings(token=None, limit=64), authorized=False) as api:
        response = await api.http.post("/api/v2/graphs", json={"document": graph_document(J1)})
        assert error(response) == (413, "request_too_large")


@pytest.mark.parametrize(("token", "mode"), [(TOKEN, "token"), (None, "none")])
async def test_the_access_mode_needs_no_token(token: str | None, mode: str) -> None:
    async with operator_api(settings=http_settings(token=token), authorized=False) as api:
        for headers in ({}, BROWSER, {"host": "localhost:8000"}):
            response = await api.http.get("/api/v2/access", headers=headers)
            assert (response.status_code, response.json()) == (200, {"authentication": mode})
            assert response.headers["cache-control"] == "no-store"
        assert error(await api.http.get("/api/v2/access?mode=1")) == (422, "invalid_query")


async def test_other_access_requests_answer_like_unknown_routes() -> None:
    async with operator_api(authorized=False) as api:
        bearer = {"authorization": f"Bearer {TOKEN}"}
        for method, path in [("POST", "/api/v2/access"), ("GET", "/api/v2/access/")]:
            anonymous = await api.http.request(method, path)
            assert error(anonymous) == (401, "operator_authentication_required")
            assert error(await api.http.request(method, path, headers=bearer)) == (404, "not_found")
    async with operator_api(settings=OPEN, authorized=False) as api:
        assert error(await api.http.post("/api/v2/access")) == (404, "not_found")


async def test_without_an_operator_token_component_endpoints_still_need_a_grant() -> None:
    async with operator_api(settings=OPEN, authorized=False) as api:
        body = {"model": LUNA, "messages": [{"role": "user", "content": "Hi"}]}
        completion = await api.http.post("/v1/chat/completions", json=body)
        assert error(completion) == (401, "invalid_grant")
        headers = {key: value for key, value in raw_headers("").items() if key != "authorization"}
        content = raw_call('{"kind": "step", "content": 1}')
        report = await api.http.post("/mcp", content=content, headers=headers)
        assert error(report) == (401, "invalid_grant")
