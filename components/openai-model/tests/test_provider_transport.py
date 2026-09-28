"""The upstream boundary keeps native evidence, bounded capture and uncertain outcomes."""

import time

import httpx2
import pytest
from slow_thinker_host import Invocation, JsonObject, json_object, validate_value
from slow_thinker_openai_model import (
    ModelConfig,
    OpenAIModelHost,
    ProviderEndpoint,
    ProviderTransport,
    effective_operation,
)
from support.native_model import response

CONFIG = ModelConfig("bound-model", "gpt-6-luna", 8, 32)
SECRET = "resource-test-secret"
ARGUMENTS: JsonObject = {
    "request": {"model": "bound-model", "messages": [{"role": "user", "content": "hello"}]}
}


def host(transport: httpx2.AsyncBaseTransport, *, limit: int = 524_288) -> OpenAIModelHost:
    endpoint = ProviderEndpoint("https://api.openai.com/v1", SECRET, max_response_bytes=limit)
    return OpenAIModelHost(
        CONFIG, effective_operation(CONFIG), ProviderTransport(endpoint, transport)
    )


@pytest.mark.parametrize("status", [200, 400, 401, 403, 404, 422, 429, 500, 503])
async def test_one_attempt_preserves_provider_evidence(status: int) -> None:
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        return httpx2.Response(
            status,
            json=response() if status == 200 else {"error": {"code": "fixture"}},
            headers={"x-request-id": "req_1", "retry-after": "10"},
        )

    resource = host(httpx2.MockTransport(handle))
    result = await resource.invoke(
        "complete", ARGUMENTS, Invocation("scoped-grant", time.monotonic() + 5)
    )
    assert len(calls) == 1 and calls[0].headers["authorization"] == f"Bearer {SECRET}"
    assert b"scoped-grant" not in calls[0].content and result.is_error == (status != 200)
    validate_value(result.value, effective_operation(CONFIG).output_schema)
    evidence = result.value if status == 200 else json_object(result.value["error"])
    assert evidence["request_id"] == "req_1"
    if status != 200:
        assert evidence["status"] == status and evidence["origin"] == "provider"
        assert evidence["retry_after"] == "10"


@pytest.mark.parametrize("fault", ["timeout", "size", "redirect", "nonjson", "invalid_success"])
async def test_unknown_or_invalid_outcomes_are_not_reported_as_success(fault: str) -> None:
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        if fault == "timeout":
            raise httpx2.ReadTimeout(SECRET, request=request)
        if fault == "redirect":
            return httpx2.Response(307, headers={"location": "https://other.example"})
        return httpx2.Response(
            200, content=b"x" * 100 if fault == "size" else b"bad" if fault == "nonjson" else b"[]"
        )

    result = await host(httpx2.MockTransport(handle), limit=50).invoke(
        "complete", ARGUMENTS, Invocation("grant", time.monotonic() + 5)
    )
    assert len(calls) == 1 and result.is_error and SECRET not in str(result)
    evidence = json_object(result.value["error"])
    assert evidence["origin"] == ("transport" if fault in {"size", "timeout"} else "protocol")


async def test_provider_credential_reflection_is_redacted_before_returning() -> None:
    def handle(request: httpx2.Request) -> httpx2.Response:
        del request
        return httpx2.Response(
            400,
            json={"error": {"message": SECRET, "nested": [SECRET, 1]}},
            headers={"x-request-id": SECRET, "retry-after": SECRET},
        )

    result = await host(httpx2.MockTransport(handle)).invoke(
        "complete", ARGUMENTS, Invocation("grant", time.monotonic() + 5)
    )
    assert result.is_error and result.value["redacted"] is True
    assert SECRET not in str(result) and "[redacted]" in str(result)


@pytest.mark.parametrize(
    "context",
    [
        Invocation("grant"),
        Invocation("", 1),
        Invocation("grant", 1),
        Invocation("grant", float("nan")),
    ],
)
async def test_missing_or_expired_authority_never_dispatches(context: Invocation) -> None:
    def handle(request: httpx2.Request) -> httpx2.Response:
        del request
        pytest.fail("Invalid invocation must never send an upstream request")

    with pytest.raises((ValueError, TimeoutError)):
        await host(httpx2.MockTransport(handle)).invoke("complete", ARGUMENTS, context)
