"""`/mcp` admits non-browser requests at revision 2026-07-28 whose grant names an active call."""

from dataclasses import replace

import pytest
from slow_thinker_ii.application import InvalidGrant, ReportService
from slow_thinker_ii.contracts import JsonValue

from .http_harness import error, held_call, held_platform, http_settings, operator_api, services
from .http_mcp import call, raw_call, raw_headers, report_client, tool_error

REPORT = raw_call('{"kind": "step", "content": 1}')
CHANGES = {
    "unknown": {"authorization": "Bearer unknown-grant"},
    "basic": {"authorization": "Basic dXNlcjpwYXNz"},
    "origin": {"origin": "http://127.0.0.1:5173"},
    "version": {"mcp-protocol-version": "2025-11-25"},
}
REMOVED = {"missing": "authorization", "unversioned": "mcp-protocol-version"}


@pytest.mark.parametrize(
    ("mode", "status", "code"),
    [
        ("missing", 401, "invalid_grant"),
        ("unknown", 401, "invalid_grant"),
        ("basic", 401, "invalid_grant"),
        ("origin", 403, "browser_origin_denied"),
        ("query", 400, "invalid_request"),
        ("version", 400, "unsupported_protocol"),
        ("unversioned", 400, "unsupported_protocol"),
    ],
)
async def test_refused_requests_reach_no_tool(mode: str, status: int, code: str) -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        headers = raw_headers(context.grant) | CHANGES.get(mode, {})
        path = "/mcp?debug=1" if mode == "query" else "/mcp"
        request = api.http.build_request("POST", path, content=REPORT, headers=headers)
        if mode in REMOVED:
            del request.headers[REMOVED[mode]]
        response = await api.http.send(request)
        assert error(response) == (status, code)
        assert api.platform.run_store.of(context.run_id, "report") == []


async def test_the_grant_of_an_ended_call_is_refused() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        api.platform.runs.stop(context.run_id)
        await api.platform.finish(context.run_id)
        response = await api.http.post("/mcp", content=REPORT, headers=raw_headers(context.grant))
        assert error(response) == (401, "invalid_grant")
        assert response.json()["error"]["type"] == "authentication_error"


class EndedCalls(ReportService):
    """Reports whose call ends between the request's admission and the tool call."""

    def report(self, grant: str, kind: str, content: JsonValue) -> None:
        del grant, kind, content
        raise InvalidGrant()


async def test_a_call_ending_after_admission_is_an_invalid_grant_tool_error() -> None:
    platform, hosts = held_platform()
    ended = replace(services(platform), reports=EndedCalls(platform.runs))
    async with operator_api(platform, http_services=ended) as api:
        context = await held_call(api, hosts)
        async with report_client(api.app, context.grant) as client:
            result = await call(client, {"kind": "step", "content": 1})
        assert tool_error(result) == "invalid_grant"


async def test_report_requests_are_bounded_posts() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform, settings=http_settings(limit=64)) as api:
        context = await held_call(api, hosts)
        headers = raw_headers(context.grant)
        assert (await api.http.post("/mcp", content=REPORT, headers=headers)).status_code == 413
        assert (await api.http.get("/mcp", headers=headers)).status_code == 405
        assert api.platform.run_store.of(context.run_id, "report") == []
