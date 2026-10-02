"""One shared production composition passes before parallel acceptance expansion."""

from pathlib import Path

import httpx
import pytest
from slow_thinker_ii.adapters.catalog import GraphDefinitionValidator
from slow_thinker_ii.contracts import decode_json, json_object
from support.sequence_plans import EXAMPLES, SCHEMAS
from support.workspace_data import field_strings, workspace_descriptors
from support.workspace_http import workspace_http


async def assert_source_patch(client: httpx.AsyncClient) -> None:
    patched = await client.post(
        "/api/v1/definitions/patch",
        json={
            "source": '{"extension":9007199254740993,"fraction":1.0,"name":"old"}',
            "operations": [{"op": "replace", "path": "/name", "value_json": '"new"'}],
        },
    )
    assert patched.status_code == 200
    assert json_object(decode_json(patched.text))["extension"] == 9007199254740993
    assert '"fraction":1.0' in patched.text


@pytest.mark.asyncio
async def test_workspace_discovery_patch_and_settings_are_composable(tmp_path: Path) -> None:
    case = workspace_http(tmp_path)
    async with case.client as client:
        discovery = await client.get("/api/v1/configuration/catalog")
        assert discovery.status_code == 200
        catalog = json_object(discovery.json())
        types = field_strings(catalog["components"], "type_id")
        assert {
            "contextual-call",
            "calculator",
            "key-value-memory",
            "example.resource-agent",
        } <= types
        await assert_source_patch(client)
        body = {
            "command_id": "a" * 32,
            "expected_revision": "workspace-1",
            "limits": {"call_seconds": 10},
        }
        receipt = await client.post("/api/v1/configuration/limits", json=body)
        assert receipt.status_code == 200
        replay = await client.post("/api/v1/configuration/limits", json=body)
        assert replay.json()["replayed"] is True
        selected = case.base.store.profile()
        assert selected is not None and selected.limits.call_seconds == 10


def test_registered_resource_collaboration_definition_is_valid() -> None:
    validator = GraphDefinitionValidator(SCHEMAS, EXAMPLES, workspace_descriptors())
    source = (EXAMPLES / "resource-collaboration.graph.json").read_text()
    definition = validator.validate(source)
    assert "example.resource-agent" in definition.definition_json
    detail = json_object(decode_json(validator.detail(source)))
    assert detail["graph_id"] == "resource-collaboration"
