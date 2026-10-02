"""UTF-8 byte bounds apply to complete raw source/draft responses and streamed bodies."""

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Never

import pytest
from slow_thinker_ii.application import library
from support.definition_http import (
    ROOT,
    DefinitionHttp,
    definition_http,
    error_data,
    reference,
    variant,
)


async def test_draft_response_bound_rejects_complete_large_graph(tmp_path: Path) -> None:
    case = definition_http(tmp_path, 256)
    case.service.save(variant())
    try:
        response = await case.client.post(
            ROOT + "/draft", json={"source": reference(), "target": reference("new")}
        )
        error_data(response, 413, "response_too_large")
    finally:
        await case.client.aclose()


async def test_utf8_request_and_source_bounds_count_bytes(tmp_path: Path) -> None:
    source = variant("界" * 10)
    case = definition_http(tmp_path, len(source))
    case.service.save(source)
    try:
        response = await case.client.get(ROOT + "/source", params=reference("界" * 10))
        error_data(response, 413, "response_too_large")
        response = await case.client.post(
            ROOT, content=chunks(source.encode()), headers={"content-type": "application/json"}
        )
        error_data(response, 413, "request_too_large")
    finally:
        await case.client.aclose()


async def chunks(body: bytes) -> AsyncIterator[bytes]:
    for offset in range(0, len(body), 17):
        yield body[offset : offset + 17]


async def test_unknown_application_error_codes_are_not_exposed(
    definitions: DefinitionHttp, monkeypatch: pytest.MonkeyPatch
) -> None:
    def fail(_: str) -> Never:
        raise library.DefinitionError("private_credential_secret")

    monkeypatch.setattr(definitions.service, "validate", fail)
    response = await definitions.client.post(ROOT + "/validate", json={})
    error_data(response, 503, "operator_service_unavailable")
    assert "credential" not in response.text and "secret" not in response.text
