"""Inspection preserves absence, bounds and authentication without trusting arbitrary references."""

from pathlib import Path

import pytest
from slow_thinker_ii.contracts import OperationResult, encode_json
from support.operator_http import HttpCase, http_case, payload
from support.operator_trace import completed_trace


@pytest.mark.parametrize(
    "identity",
    [
        "missing",
        "event:",
        "event:-1",
        "event:1e1",
        "event:١",
        "event:9223372036854775808",
        "event:99999999999999999999",
        "event:9999",
        "request:missing",
        "usage:missing",
        "file:secret",
        "response:missing",
    ],
)
async def test_unknown_or_malformed_payload_identity_is_not_resolved(
    api: HttpCase, identity: str
) -> None:
    run, _ = await completed_trace(api)
    response = await api.client.get(f"/api/v1/runs/{run}/payloads/{identity}")
    assert response.status_code == 404


async def test_trace_reads_require_operator_authority(api: HttpCase) -> None:
    run, call = await completed_trace(api)
    for suffix in ("events", f"calls/{call}", "payloads/event:1"):
        response = await api.client.get(
            f"/api/v1/runs/{run}/{suffix}", headers={"authorization": ""}
        )
        assert response.status_code == 401


async def test_large_payload_is_explicitly_rejected_without_breaking_metadata_pages(
    tmp_path: Path,
) -> None:
    api = http_case(tmp_path, limit=2500)
    api.case.preparer.operation.result = OperationResult(encode_json({"text": "x" * 4000}), False)
    try:
        run, call = await completed_trace(api)
        details = payload(await api.client.get(f"/api/v1/runs/{run}/calls/{call}"))
        identity = "response:" + str(details["result_receipt_id"])
        response = await api.client.get(f"/api/v1/runs/{run}/payloads/{identity}")
        assert response.status_code == 413
        assert "response_too_large" in response.text
        assert len(api.case.preparer.operation.calls) == 1
    finally:
        await api.close()
