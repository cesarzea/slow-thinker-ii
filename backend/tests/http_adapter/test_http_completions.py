"""`/v1/chat/completions` passes the gateway's reply on unchanged and refuses unsafe transport."""

from dataclasses import replace

import pytest
from slow_thinker_ii.application import GatewayReply, LlmGateway
from slow_thinker_ii.contracts import JsonObject
from support.examples import FLASH, LUNA
from support.platform import Platform

from .http_harness import error, held_call, held_platform, http_settings, operator_api, services

URL = "/v1/chat/completions"
REQUEST: JsonObject = {"model": LUNA, "messages": [{"role": "user", "content": "Hi"}]}
INVALID = "invalid_request_error"
TYPES = {
    400: INVALID,
    401: "authentication_error",
    403: "permission_error",
    413: INVALID,
    415: INVALID,
}
UNSELECTED = f'{{"model": "{FLASH}", "messages": [{{"role": "user", "content": "Hi"}}]}}'
NOT_SELECTED = f"The model “{FLASH}” is not selected in this component's configuration."
NO_STREAMING = 'Streaming is not supported; send "stream": false or omit it.'


def component(grant: str) -> dict[str, str]:
    return {"authorization": f"Bearer {grant}", "content-type": "application/json"}


async def test_a_component_call_is_answered_by_the_gateway() -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        response = await api.http.post(URL, json=REQUEST, headers=component(context.grant))
        assert response.status_code == 200
        assert response.json()["choices"][0]["message"]["content"] == "Simulated reply to: Hi"
        [called] = api.platform.run_store.of(context.run_id, "llm.called")
        assert called.data["response"] == response.json()


@pytest.mark.parametrize(
    ("content", "status", "code", "message"),
    [
        (UNSELECTED, 403, "model_not_allowed", NOT_SELECTED),
        (
            '{"model": "a", "model": "b"}',
            400,
            "invalid_request",
            "The request body is not valid JSON.",
        ),
        ('{"stream": true}', 400, "invalid_request", NO_STREAMING),
    ],
)
async def test_gateway_refusals_are_passed_on_unchanged(
    content: str, status: int, code: str, message: str
) -> None:
    platform, hosts = held_platform()
    async with operator_api(platform) as api:
        context = await held_call(api, hosts)
        response = await api.http.post(URL, content=content, headers=component(context.grant))
        expected = {"code": code, "message": message, "type": TYPES[status]}
        assert (response.status_code, response.json()) == (status, {"error": expected})
        [called] = api.platform.run_store.of(context.run_id, "llm.called")
        assert called.data["error"] == expected
        assert api.platform.provider.requests == []


async def test_an_unknown_grant_gets_the_gateway_401() -> None:
    async with operator_api() as api:
        response = await api.http.post(URL, json=REQUEST, headers=component("unknown-grant"))
        message = "The grant is missing, unknown or expired."
        expected = {"code": "invalid_grant", "message": message, "type": "authentication_error"}
        assert (response.status_code, response.json()) == (401, {"error": expected})


@pytest.mark.parametrize(
    ("mode", "status", "code"),
    [
        ("missing", 401, "invalid_grant"),
        ("basic", 401, "invalid_grant"),
        ("bare", 401, "invalid_grant"),
        ("spaced", 401, "invalid_grant"),
        ("origin", 403, "browser_origin_denied"),
        ("project", 400, "invalid_request"),
        ("query", 400, "invalid_request"),
        ("media", 415, "unsupported_media_type"),
        ("large", 413, "request_too_large"),
        ("encoding", 400, "invalid_request"),
    ],
)
async def test_refused_requests_never_reach_the_gateway(mode: str, status: int, code: str) -> None:
    platform, hosts = held_platform()
    async with operator_api(platform, settings=http_settings(limit=128)) as api:
        context = await held_call(api, hosts)
        headers = component(context.grant) | CHANGES.get(mode, {})
        content = {"large": b"{" + b" " * 128 + b"}", "encoding": b'"\xff"'}.get(mode, b"{}")
        path = f"{URL}?stream=true" if mode == "query" else URL
        request = api.http.build_request("POST", path, content=content, headers=headers)
        if mode == "missing":
            del request.headers["authorization"]
        response = await api.http.send(request)
        assert error(response) == (status, code)
        assert response.json()["error"]["type"] == TYPES[status]
        assert api.platform.run_store.of(context.run_id, "llm.called") == []


CHANGES = {
    "basic": {"authorization": "Basic dXNlcjpwYXNz"},
    "bare": {"authorization": "Bearer"},
    "spaced": {"authorization": "Bearer one two"},
    "origin": {"origin": "null"},
    "project": {"openai-project": "other"},
    "media": {"content-type": "text/plain"},
}


class FailingGateway(LlmGateway):
    async def complete(self, grant: str, body: str) -> GatewayReply:
        del grant, body
        raise OSError("The run store is unavailable.")


async def test_unexpected_failures_answer_an_api_error() -> None:
    platform = Platform()
    gateway = FailingGateway(
        runs=platform.runs,
        ledger=platform.ledger,
        provider=platform.provider,
        models=(),
        budgets=platform.budgets,
        clock=platform.clock,
    )
    failing = replace(services(platform), gateway=gateway)
    async with operator_api(platform, http_services=failing, raise_errors=False) as api:
        response = await api.http.post(URL, json=REQUEST, headers=component("grant"))
        message = "The server could not complete the request."
        expected = {"code": "internal_error", "message": message, "type": "api_error"}
        assert (response.status_code, response.json()) == (500, {"error": expected})
