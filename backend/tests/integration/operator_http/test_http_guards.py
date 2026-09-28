"""Reject foreign browser authority, malformed commands and oversized content before execution."""

from pathlib import Path

import pytest
from support.operator_http import TOKEN, HttpCase, http_case, payload


@pytest.mark.parametrize(
    "header,value,status",
    [
        ("authorization", "Bearer wrong", 401),
        ("authorization", "", 401),
        ("host", "evil.example", 403),
        ("host", "127.0.0.1:9000", 403),
        ("origin", "http://evil.example", 403),
        ("origin", "null", 403),
        ("sec-fetch-site", "cross-site", 403),
    ],
)
async def test_untrusted_requests_never_prepare(
    api: HttpCase, header: str, value: str, status: int
) -> None:
    response = await api.client.post("/api/v1/runs", json=api.start(), headers={header: value})
    assert response.status_code == status
    assert not api.case.preparer.calls
    assert TOKEN not in response.text
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.parametrize("header", ["authorization", "origin", "host"])
async def test_duplicate_security_headers(api: HttpCase, header: str) -> None:
    value = api.client.headers[header] if header != "host" else "127.0.0.1:8000"
    response = await api.client.get("/api/v1/workspace", headers=[(header, value), (header, value)])
    assert response.status_code in (401, 403)


@pytest.mark.parametrize(
    "content,status",
    [
        ('{"schema_version":"0.1-draft","command_id":"x","command_id":"y"}', 400),
        ('{"command_id":NaN}', 400),
        ("[]", 400),
        ("{", 400),
        ('{"schema_version":"0.1-draft","command_id":"start"}', 422),
    ],
)
async def test_invalid_body(api: HttpCase, content: str, status: int) -> None:
    response = await api.client.post(
        "/api/v1/runs", content=content, headers={"content-type": "application/json"}
    )
    assert response.status_code == status
    assert not api.case.preparer.calls


async def test_extra_authority_fields_are_rejected(api: HttpCase) -> None:
    body = api.start()
    body["snapshot_json"] = "forged runtime"
    assert (await api.client.post("/api/v1/runs", json=body)).status_code == 422
    assert not api.case.preparer.calls


async def test_oversized_stream_is_bounded(tmp_path: Path) -> None:
    api = http_case(tmp_path, limit=64)
    try:
        response = await api.client.post("/api/v1/runs", json=api.start())
        assert response.status_code == 413 and not api.case.preparer.calls
    finally:
        await api.close()


@pytest.mark.parametrize(
    "url",
    [
        "/api/v1/runs/missing",
        "/api/v1/runs/missing/definition",
        "/api/v1/commands/missing",
        "/api/v1/sessions/missing/runs",
    ],
)
async def test_unknown_objects_are_not_found(api: HttpCase, url: str) -> None:
    response = await api.client.get(url)
    assert response.status_code == 404
    assert payload(response)["error"]


async def test_error_diagnostics_do_not_include_internal_paths(api: HttpCase) -> None:
    api.case.preparer.failure = None
    await api.case.coordinator.close()
    response = await api.client.post("/api/v1/runs", json=api.start())
    assert response.status_code == 503
    assert "/Users/" not in response.text and "Traceback" not in response.text
