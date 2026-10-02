"""Production lifespan activates trusted configuration and protects owned execution on shutdown."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slow_thinker_ii.adapters.sqlite import SqliteConfigurationCommands, SqliteDatabase
from slow_thinker_ii.application import (
    CoordinatorShutdown,
    ExecutionConfiguration,
    ExecutionCoordinator,
)
from slow_thinker_ii.bootstrap import create_app
from support.application_setup import application_setup
from support.catalog import RecordedCatalog
from support.operator_http import ORIGIN, TOKEN, payload

HEADERS = {"authorization": "Bearer " + TOKEN, "origin": ORIGIN}


def test_application_activates_operator_and_native_routes(tmp_path: Path) -> None:
    setup = application_setup(tmp_path)
    app = create_app(tmp_path / "app.sqlite", RecordedCatalog(), setup)
    with TestClient(app, base_url=ORIGIN, headers=HEADERS) as client:
        workspace = client.get("/api/v1/workspace")
        assert workspace.status_code == 200
        assert payload(workspace)["configuration_revision"] == setup.configuration.revision
        body = {"schema_version": "0.1-draft", "command_id": "session", "name": "Research"}
        assert client.post("/api/v1/sessions", json=body).status_code == 202
        native = client.post("/v1/chat/completions", json={})
        assert (
            native.status_code == 403
        )  # Browser-origin operator authority is not a component grant.
        client.headers.pop("origin")
        assert client.post("/v1/chat/completions", json={}).status_code == 403
    with SqliteDatabase(tmp_path / "app.sqlite").ownership():
        pass


def test_failed_startup_releases_database_ownership(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    setup = application_setup(tmp_path)

    def failed(self: SqliteConfigurationCommands, profile: ExecutionConfiguration) -> None:
        del self, profile
        raise RuntimeError("Synthetic activation failure")

    monkeypatch.setattr(SqliteConfigurationCommands, "initialize", failed)
    app = create_app(tmp_path / "app.sqlite", RecordedCatalog(), setup)
    with (
        pytest.raises(RuntimeError, match="Synthetic activation failure"),
        TestClient(app, base_url=ORIGIN),
    ):
        pass
    with SqliteDatabase(tmp_path / "app.sqlite").ownership():
        pass


def test_incomplete_shutdown_does_not_release_owned_database(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    async def incomplete(self: ExecutionCoordinator) -> CoordinatorShutdown:
        del self
        return CoordinatorShutdown(("still-committing",), (), ())

    monkeypatch.setattr(ExecutionCoordinator, "close", incomplete)
    app = create_app(tmp_path / "app.sqlite", RecordedCatalog(), application_setup(tmp_path))
    with pytest.raises(RuntimeError, match="ownership retained"), TestClient(app, base_url=ORIGIN):
        pass
    with (
        pytest.raises(RuntimeError, match="Another backend"),
        SqliteDatabase(tmp_path / "app.sqlite").ownership(),
    ):
        pytest.fail("Unfinished runtime work still owns the store")
