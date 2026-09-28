"""The actual HTTP projection preserves reused participants in all four graphs."""

from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import TypeAdapter
from slow_thinker_ii.adapters.http import GraphReply
from slow_thinker_ii.bootstrap import create_app
from support.catalog import RecordedCatalog


def test_bundled_catalog_over_http(tmp_path: Path) -> None:
    app = create_app(tmp_path / "test.sqlite", RecordedCatalog())
    with TestClient(app, base_url="http://127.0.0.1") as client:
        response = client.get("/api/v1/graphs")
    assert response.status_code == 200
    body = TypeAdapter(list[GraphReply]).validate_json(response.content)
    assert [len(graph.nodes) for graph in body] == [1, 2, 3, 5]
    review = body[2]
    assert review.participants == 2
    assert [node.component for node in review.nodes] == ["proposer", "reviewer", "proposer"]
    assert len({node.id for node in review.nodes}) == 3


def test_untrusted_host_is_rejected(tmp_path: Path) -> None:
    app = create_app(tmp_path / "test.sqlite", RecordedCatalog())
    with TestClient(app, base_url="http://foreign.example") as client:
        response = client.get("/api/v1/graphs")
    assert response.status_code == 400
