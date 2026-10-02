"""Workspace transport is authorized, bounded and returns stable redacted errors."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.workspace import WorkspaceCatalog
from support.definition_http import error_data
from support.workspace_http import workspace_http

ROOT = "/api/v1"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "path, body, code",
    [
        ("configuration/limits", [], "invalid_limits"),
        ("configuration/limits", {}, "invalid_limits"),
        ("definitions/patch", [], "invalid_patch"),
        ("definitions/patch", {"source": "{}", "operations": [1]}, "invalid_patch"),
        (
            "definitions/patch",
            {"source": "[]", "operations": [{"op": "remove", "path": "/a"}]},
            "invalid_patch",
        ),
        ("definitions/patch", {"source": "{}", "operations": [], "unknown": True}, "invalid_patch"),
    ],
)
async def test_invalid_workspace_payload(
    tmp_path: Path, path: str, body: object, code: str
) -> None:
    case = workspace_http(tmp_path)
    async with case.client as client:
        error_data(await client.post(f"{ROOT}/{path}", json=body), 422, code)


@pytest.mark.asyncio
@pytest.mark.parametrize("path", ["configuration/limits", "definitions/patch"])
async def test_workspace_transport_json_and_authentication(tmp_path: Path, path: str) -> None:
    case = workspace_http(tmp_path)
    async with case.client as client:
        response = await client.post(
            f"{ROOT}/{path}", content="{", headers={"content-type": "application/json"}
        )
        error_data(response, 400, "invalid_json")
        response = await client.post(f"{ROOT}/{path}", content="{}")
        error_data(response, 415, "json_content_required")
        client.headers.pop("authorization")
        assert (await client.post(f"{ROOT}/{path}", json={})).status_code == 401
        assert (await client.get(f"{ROOT}/configuration/catalog")).status_code == 401


@pytest.mark.asyncio
async def test_discovery_queries_bounds_and_unexpected_errors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    case = workspace_http(tmp_path)
    async with case.client as client:
        error_data(
            await client.get(f"{ROOT}/configuration/catalog?unknown=1"), 400, "invalid_query"
        )

        def fail(self: WorkspaceCatalog) -> None:
            del self
            raise RuntimeError("private/secret/key")

        monkeypatch.setattr(WorkspaceCatalog, "read", fail)
        failed = await client.get(f"{ROOT}/configuration/catalog")
        error_data(failed, 503, "operator_service_unavailable")
        assert "private/secret/key" not in failed.text
    monkeypatch.undo()
    bounded = workspace_http(tmp_path / "bounded", 64)
    async with bounded.client as client:
        error_data(await client.get(f"{ROOT}/configuration/catalog"), 413, "response_too_large")
        error_data(
            await client.post(
                f"{ROOT}/definitions/patch", json={"source": "x" * 65, "operations": []}
            ),
            413,
            "request_too_large",
        )


@pytest.mark.asyncio
async def test_settings_conflict_and_ceiling_wire_codes(tmp_path: Path) -> None:
    case = workspace_http(tmp_path)
    async with case.client as client:
        body = {
            "command_id": "a" * 32,
            "expected_revision": "workspace-1",
            "limits": {"max_depth": 9},
        }
        error_data(
            await client.post(f"{ROOT}/configuration/limits", json=body), 422, "invalid_limits"
        )
        body["limits"] = {"max_depth": 4}
        assert (await client.post(f"{ROOT}/configuration/limits", json=body)).status_code == 200
        body["command_id"] = "b" * 32
        error_data(
            await client.post(f"{ROOT}/configuration/limits", json=body),
            409,
            "configuration_conflict",
        )
