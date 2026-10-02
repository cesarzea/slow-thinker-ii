"""Discovery preserves trusted schemas and distinguishes validity from availability."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import ComponentCatalog
from slow_thinker_ii.adapters.sqlite import SqliteModelTariffStore, SqliteTariffStore
from slow_thinker_ii.adapters.tariffs import parse_catalog, parse_deepseek_pricing
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.catalog import PAYLOAD
from support.sequence_plans import EXAMPLES, SCHEMAS
from support.workspace_data import field_strings, objects, workspace_descriptors
from support.workspace_http import WorkspaceHttp, workspace_http
from support.workspace_tariffs import DEEPSEEK_PAYLOAD


def configure_discovery(case: WorkspaceHttp, clock: int, expiry: int) -> None:
    case.base.wall.value = clock
    value = json_object(decode_json(case.profile.resources_json))
    providers = json_object(value["providers"])
    value["providers"] = {
        name: {**json_object(item), "review_expires_at": expiry} for name, item in providers.items()
    }
    value["installations"] = [objects(value["installations"])[0]]
    selected = replace(
        case.profile,
        revision=f"discovery-{clock}-{expiry}",
        resources_json=encode_json(value),
    )
    case.base.store.configure(selected)


def assert_discovery(source: str, expected: str) -> None:
    result = json_object(decode_json(source))
    assert field_strings(result["models"], "tariff_status") == {expected}
    assert any(
        item["installation_status"] == "unavailable" for item in objects(result["components"])
    )
    assert "credential_ref" not in source and "base_url" not in source
    assert result["schema_documents"] and result["graph_schema"]


@pytest.mark.asyncio
async def test_review_expired_stale_ready_models_and_unavailable_types(tmp_path: Path) -> None:
    case = workspace_http(tmp_path)
    now = int(case.base.wall())
    SqliteTariffStore(case.base.database).publish(parse_catalog(PAYLOAD, now))
    SqliteModelTariffStore(case.base.database, "deepseek.flash.direct.v1").publish(
        parse_deepseek_pricing(DEEPSEEK_PAYLOAD, now)
    )
    async with case.client as client:
        for expected, clock, expiry in [
            ("ready", now, now + 200000),
            ("stale", now + 86401, now + 200000),
            ("review_expired", now, now - 1),
            ("stale", now - 1, now + 200000),
        ]:
            configure_discovery(case, clock, expiry)
            response = await client.get("/api/v1/configuration/catalog")
            assert response.status_code == 200
            assert_discovery(response.text, expected)


def test_catalogue_exact_duplicate_and_conflicting_external_descriptor() -> None:
    sources = workspace_descriptors()
    catalog = ComponentCatalog(SCHEMAS, EXAMPLES, (*sources, sources[0]))
    components = catalog.components()
    assert sum(item["type_id"] == "model-provider" for item in components) == 1
    changed = json_object(decode_json(sources[0]))
    changed["config_schema"] = {"type": "object"}
    with pytest.raises(ValueError):
        ComponentCatalog(SCHEMAS, EXAMPLES, (*sources, encode_json(changed)))


@pytest.mark.asyncio
async def test_missing_active_profile_discovery_is_unavailable(tmp_path: Path) -> None:
    case = workspace_http(tmp_path)
    with case.base.database.transaction() as db:
        db.execute("UPDATE operator_workspace SET profile_revision=NULL")
    async with case.client as client:
        reply = await client.get("/api/v1/configuration/catalog")
        assert reply.status_code == 503
        assert reply.json()["error"]["code"] == "operator_service_unavailable"
