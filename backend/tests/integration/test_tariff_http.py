"""Price availability and failure remain observable through the actual application."""

from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from slow_thinker_ii.adapters.http import TariffStatusReply
from slow_thinker_ii.bootstrap import create_app
from support.catalog import RecordedCatalog


def test_prices_survive_application_restart_without_download(tmp_path: Path) -> None:
    source = RecordedCatalog()
    path = tmp_path / "app.sqlite"
    with TestClient(create_app(path, source), base_url="http://127.0.0.1") as client:
        first = TypeAdapter(TariffStatusReply).validate_json(client.get("/api/v1/tariffs").content)
    assert first.revision is not None
    assert first.currency == "USD"
    assert first.stale is False
    with TestClient(create_app(path, source), base_url="http://127.0.0.1") as client:
        second = TypeAdapter(TariffStatusReply).validate_json(client.get("/api/v1/tariffs").content)
    assert second == first
    assert source.calls == 1


def test_missing_catalogue_does_not_prevent_graph_inspection(tmp_path: Path) -> None:
    source = RecordedCatalog()
    source.error = OSError("unreachable")
    app = create_app(tmp_path / "app.sqlite", source)
    with TestClient(app, base_url="http://127.0.0.1") as client:
        prices = client.get("/api/v1/tariffs")
        assert client.get("/api/v1/graphs").status_code == 200
    status = TypeAdapter(TariffStatusReply).validate_json(prices.content)
    assert status.revision is None
    assert status.stale is True
    assert status.refresh_error == "OSError"
