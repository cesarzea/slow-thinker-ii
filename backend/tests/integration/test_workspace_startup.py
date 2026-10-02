"""Configured lifespans refresh independent sources and retain durable user settings."""

from dataclasses import replace
from pathlib import Path

from fastapi.testclient import TestClient
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteModelTariffReader
from slow_thinker_ii.bootstrap import ExecutionSetup, create_app
from slow_thinker_ii.contracts import encode_json
from support.application_setup import application_setup
from support.catalog import RecordedCatalog
from support.operator_http import ORIGIN, TOKEN
from support.workspace_data import workspace_descriptors, workspace_resources
from support.workspace_tariffs import RecordedDeepSeek

HEADERS = {"authorization": "Bearer " + TOKEN, "origin": ORIGIN}


def configured_setup(tmp_path: Path) -> ExecutionSetup:
    setup = application_setup(tmp_path)
    return replace(
        setup,
        configuration=replace(
            setup.configuration, resources_json=encode_json(workspace_resources())
        ),
        descriptors=workspace_descriptors(),
    )


def save_limits(client: TestClient, revision: str) -> tuple[dict[str, object], str]:
    body: dict[str, object] = {
        "command_id": "a" * 32,
        "expected_revision": revision,
        "limits": {"call_seconds": 10},
    }
    receipt = client.post("/api/v1/configuration/limits", json=body)
    assert receipt.status_code == 200
    selected: object = receipt.json()["configuration_revision"]
    assert isinstance(selected, str)
    return body, selected


def test_two_automatic_sources_and_settings_survive_backend_restart(tmp_path: Path) -> None:
    setup = configured_setup(tmp_path)
    openai, deepseek = RecordedCatalog(), RecordedDeepSeek()
    database = tmp_path / "application.sqlite"
    app = create_app(database, openai, setup, {"deepseek.flash.direct.v1": deepseek})
    with TestClient(app, base_url=ORIGIN, headers=HEADERS) as client:
        discovery = client.get("/api/v1/configuration/catalog")
        assert discovery.status_code == 200
        assert {item["tariff_status"] for item in discovery.json()["models"]} == {"ready"}
        body, revision = save_limits(client, setup.configuration.revision)
    assert openai.calls == deepseek.calls == 1
    with TestClient(
        create_app(database, openai, setup, {"deepseek.flash.direct.v1": deepseek}),
        base_url=ORIGIN,
        headers=HEADERS,
    ) as client:
        discovery = client.get("/api/v1/configuration/catalog").json()
        assert discovery["configuration_revision"] == revision
        assert discovery["limits"]["current"]["call_seconds"] == 10
        assert client.post("/api/v1/configuration/limits", json=body).json()["replayed"]
    assert openai.calls == deepseek.calls == 1


def test_missing_second_source_does_not_replace_first_prices(tmp_path: Path) -> None:
    setup = configured_setup(tmp_path)
    openai, deepseek = RecordedCatalog(), RecordedDeepSeek()
    deepseek.error = ValueError("Changed official semantics")
    database = tmp_path / "application.sqlite"
    with TestClient(
        create_app(database, openai, setup, {"deepseek.flash.direct.v1": deepseek}),
        base_url=ORIGIN,
        headers=HEADERS,
    ) as client:
        models = client.get("/api/v1/configuration/catalog").json()["models"]
        assert {item["tariff_status"] for item in models if item["provider"] == "openai"} == {
            "ready"
        }
        assert {item["tariff_status"] for item in models if item["provider"] == "deepseek"} == {
            "unavailable"
        }
    reader = SqliteModelTariffReader(SqliteDatabase(database))
    assert reader.selected("deepseek.flash.direct.v1") is None
    assert reader.selected("openai.gpt-6-luna.standard.text.v1") is not None
