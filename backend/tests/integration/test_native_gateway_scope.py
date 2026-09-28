"""Native routing cannot recover expired authority or expand a caller's resource scope."""

from pathlib import Path

import httpx
import pytest
from slow_thinker_ii.contracts import JsonObject, OperationResult, encode_json
from support.native_gateway import native_case
from support.native_server import gateway_app
from support.run_admission import outstanding


@pytest.mark.parametrize("fault", ["revoked", "binding", "duplicate", "invalid", "option"])
async def test_scope_or_request_failure_never_reaches_the_model(tmp_path: Path, fault: str) -> None:
    case = native_case(tmp_path)
    body = '{"model":"bound-model","messages":[{"role":"user","content":"x"}]}'
    headers = [
        ("authorization", f"Bearer {case.parent.token}"),
        ("content-type", "application/json"),
    ]
    if fault == "revoked":
        case.run.authority.finish(case.parent.context.call_id, succeeded=True)
    elif fault == "binding":
        body = body.replace("bound-model", "another-model")
    elif fault == "duplicate":
        headers.append(headers[0])
    elif fault == "invalid":
        body = '{"model":"bound-model","model":"bound-model"}'
    else:
        body = body[:-1] + ',"temperature":0}'
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(case.gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post("/v1/chat/completions", content=body, headers=headers)
    expected = {"revoked": 403, "binding": 403, "duplicate": 401, "invalid": 400, "option": 400}
    assert reply.status_code == expected[fault] and not case.model.calls
    assert outstanding(case.run) == (0, 0, 0) and case.parent.token not in reply.text


@pytest.mark.parametrize("header", ["5", "bad\r\ninjected: true"])
async def test_provider_retry_metadata_cannot_inject_http_headers(
    tmp_path: Path, header: str
) -> None:
    case = native_case(tmp_path)
    error: JsonObject = {
        "origin": "provider",
        "status": 429,
        "body": {"error": {"code": "rate_limit"}},
        "request_id": header,
        "retry_after": header,
    }
    case.model.result = OperationResult(encode_json({"error": error}), True)
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=gateway_app(case.gateway)), base_url="http://127.0.0.1"
    ) as client:
        reply = await client.post(
            "/v1/chat/completions",
            json={"model": "bound-model", "messages": [{"role": "user", "content": "x"}]},
            headers={"authorization": f"Bearer {case.parent.token}"},
        )
    assert reply.status_code == 429 and "injected" not in reply.headers
    expected = header if header == "5" else None
    assert reply.headers.get("retry-after") == reply.headers.get("x-request-id") == expected
    assert len(case.model.calls) == 1 and outstanding(case.run) == (262_506_000,) * 3
    await case.calls.close(1)
