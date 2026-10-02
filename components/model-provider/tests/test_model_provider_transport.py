"""One native attempt retains evidence and never converts uncertainty into success."""

import time

import httpx2
import pytest
from model_provider_assertions import assert_native_evidence
from model_provider_fixture import SECRET, arguments, config, host, invocation, record, response
from slow_thinker_host import Invocation, json_object
from slow_thinker_model_provider import (
    ModelProviderHost,
    ProviderEndpoint,
    ProviderTransport,
    effective_operation,
)


@pytest.mark.parametrize("status", [200, 400, 401, 403, 404, 422, 429, 500, 503])
async def test_single_attempt_preserves_native_payload_headers_and_timing(status: int) -> None:
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        return httpx2.Response(
            status,
            json=response() if status == 200 else {"error": {"code": "fixture"}},
            headers={"x-request-id": "req-native", "retry-after": "10", "x-extra": "kept"},
        )

    started = time.time()
    result = await host(httpx2.MockTransport(handle)).invoke("complete", arguments(), invocation())
    assert len(calls) == 1 and calls[0].headers["authorization"] == f"Bearer {SECRET}"
    assert "scoped-model-grant" not in calls[0].content.decode()
    assert calls[0].url == "https://api.deepseek.com/chat/completions"
    assert_native_evidence(result, status, started)


@pytest.mark.parametrize(
    "fault", ["timeout", "body_size", "header_size", "redirect", "nonjson", "invalid_success"]
)
async def test_uncertain_or_protocol_failures_never_retry(fault: str) -> None:
    calls: list[httpx2.Request] = []

    def handle(request: httpx2.Request) -> httpx2.Response:
        calls.append(request)
        if fault == "timeout":
            raise httpx2.ReadTimeout(SECRET, request=request)
        if fault == "header_size":
            return httpx2.Response(200, headers={"x-extra": "x" * 100})
        if fault == "redirect":
            return httpx2.Response(307, headers={"location": "https://other.example"})
        return httpx2.Response(
            200,
            content=b"x" * 100 if fault == "body_size" else b"bad" if fault == "nonjson" else b"[]",
        )

    result = await host(httpx2.MockTransport(handle), limit=80).invoke(
        "complete", arguments(), invocation()
    )
    assert len(calls) == 1 and result.is_error and SECRET not in str(result)
    evidence = json_object(result.value["error"])
    assert evidence["origin"] == (
        "transport" if fault in {"body_size", "header_size", "timeout"} else "protocol"
    )


async def test_recursive_body_and_header_credential_reflection_is_redacted() -> None:
    def handle(request: httpx2.Request) -> httpx2.Response:
        del request
        return httpx2.Response(
            400,
            json={SECRET: {"nested": [SECRET, 1, True, None]}},
            headers={"x-request-id": SECRET, "retry-after": SECRET, SECRET: SECRET},
        )

    result = await host(httpx2.MockTransport(handle)).invoke("complete", arguments(), invocation())
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
async def test_invalid_managed_context_never_dispatches(context: Invocation) -> None:
    def handle(request: httpx2.Request) -> httpx2.Response:
        del request
        pytest.fail("Invalid managed authority cannot dispatch")

    with pytest.raises((ValueError, TimeoutError)):
        await host(httpx2.MockTransport(handle)).invoke("complete", arguments(), context)


async def test_host_validates_operation_and_schema_before_transport() -> None:
    def handle(request: httpx2.Request) -> httpx2.Response:
        del request
        pytest.fail("Invalid host operation cannot dispatch")

    resource = host(httpx2.MockTransport(handle))
    assert resource.operations() == ModelProviderHost.describe(record())
    for name, payload in [("other", arguments()), ("complete", {})]:
        with pytest.raises(ValueError):
            await resource.invoke(name, payload, invocation())
    with pytest.raises(ValueError):
        transport = ProviderTransport(
            ProviderEndpoint("deepseek", "https://api.deepseek.com", SECRET)
        )
        ModelProviderHost(config(), effective_operation(config("openai")), transport)
