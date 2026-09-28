"""Native compatibility does not bypass invocation scope, HTTP boundaries or recording."""

from pathlib import Path

import httpx
import pytest
from slow_thinker_ii.application import ModelBinding, NativeModelGateway
from slow_thinker_ii.contracts import OperationResult
from support.authority import PROPOSER
from support.native_gateway import native_case
from support.native_server import gateway_app
from support.run_admission import outstanding

REQUEST = '{"model":"bound-model","messages":[{"role":"user","content":"x"}]}'


@pytest.mark.parametrize(
    "mode,status",
    [
        ("missing", 401),
        ("foreign", 403),
        ("basic", 401),
        ("origin", 403),
        ("project", 400),
        ("query", 400),
        ("media", 415),
        ("large", 413),
    ],
)
async def test_rejected_http_requests_never_invoke_a_model(
    tmp_path: Path, mode: str, status: int
) -> None:
    case = native_case(tmp_path)
    headers = {"authorization": f"Bearer {case.parent.token}", "content-type": "application/json"}
    changes = {
        "foreign": ("authorization", "Bearer invalid"),
        "basic": ("authorization", "Basic invalid"),
        "origin": ("origin", "null"),
        "project": ("openai-project", "other"),
        "media": ("content-type", "text/plain"),
    }
    if mode == "missing":
        del headers["authorization"]
    elif mode in changes:
        key, value = changes[mode]
        headers[key] = value
    app = gateway_app(case.gateway, limit=16 if mode == "large" else 1024)
    path = "/v1/chat/completions" + ("?unsupported=1" if mode == "query" else "")
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(path, content=REQUEST, headers=headers)
    assert reply.status_code == status and not case.model.calls
    assert outstanding(case.run) == (0, 0, 0)


async def test_model_binding_does_not_grant_a_missing_operation_permission(tmp_path: Path) -> None:
    case = native_case(tmp_path)
    gateway = NativeModelGateway(
        case.run.authority, case.calls, (ModelBinding("proposer", "bound-model", PROPOSER),)
    )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/v1/chat/completions",
            content=REQUEST,
            headers={
                "authorization": f"Bearer {case.parent.token}",
                "content-type": "application/json",
            },
        )
    assert reply.status_code == 403 and not case.model.calls


async def test_no_provider_dispatch_when_recording_authorization_fails(tmp_path: Path) -> None:
    case = native_case(tmp_path)
    with case.run.database.transaction() as connection:
        connection.execute(
            "CREATE TRIGGER broken BEFORE INSERT ON run_events "
            "WHEN NEW.event='call.dispatch_authorized' "
            "BEGIN SELECT RAISE(ABORT,'fixture failure'); END"
        )
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(case.gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/v1/chat/completions",
            content=REQUEST,
            headers={
                "authorization": f"Bearer {case.parent.token}",
                "content-type": "application/json",
            },
        )
    assert reply.status_code == 503 and not case.model.calls
    assert "recording_unavailable" in reply.text
    await case.calls.close(1)
    assert outstanding(case.run) == (0, 0, 0)


async def test_bad_model_envelope_is_a_gateway_failure_not_a_bad_client_request(
    tmp_path: Path,
) -> None:
    case = native_case(tmp_path)
    case.model.result = OperationResult("{}", False)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(case.gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/v1/chat/completions",
            content=REQUEST,
            headers={
                "authorization": f"Bearer {case.parent.token}",
                "content-type": "application/json",
            },
        )
    assert reply.status_code == 502 and "invalid_model_response" in reply.text
    assert outstanding(case.run) == (262_506_000,) * 3


async def test_late_model_answer_is_settled_but_not_published(tmp_path: Path) -> None:
    case = native_case(tmp_path)

    def stop() -> None:
        case.run.service.stop("operator_stop")

    case.model.before_reply = stop
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(case.gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/v1/chat/completions",
            content=REQUEST,
            headers={
                "authorization": f"Bearer {case.parent.token}",
                "content-type": "application/json",
            },
        )
    assert reply.status_code == 409 and "success" not in reply.text
    assert outstanding(case.run) == (0, 0, 0)
    with case.run.store.begin() as transaction:
        assert all(scope.settled == 2390 for scope in transaction.scopes(case.run.keys))
