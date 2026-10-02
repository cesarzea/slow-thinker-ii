"""Production configured HTTP preserves saved authoring values through draft and replay."""

from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from slow_thinker_ii.bootstrap import create_app
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.browser_execution import BROWSER_TOKEN, BrowserExecution
from support.catalog import RecordedCatalog
from support.sequence_plans import graph_value


def numeric_source() -> str:
    value = graph_value("single-agent")
    value["revision"] = "numeric α / source"
    value["derived_from"] = {"graph_id": "single-agent", "revision": "example-2"}
    components = json_object(value["components"])
    proposer = json_object(components["proposer"])
    config = json_object(proposer["config"])
    config["parameters"] = {"temperature": 1.0, "seed": 9007199254740993}
    proposer["config"], components["proposer"] = config, proposer
    value["components"] = components
    return encode_json(value)


def test_configured_authoring_round_trip(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    origin = "http://127.0.0.1:8123"
    monkeypatch.setenv("SLOW_THINKER_TEST_API_ORIGIN", origin)
    monkeypatch.setenv("SLOW_THINKER_TEST_BROWSER_ORIGIN", origin)
    app = create_app(tmp_path / "state.sqlite", RecordedCatalog(), BrowserExecution())
    headers = {"authorization": f"Bearer {BROWSER_TOKEN}", "content-type": "application/json"}
    with TestClient(app, base_url=origin, headers=headers) as client:
        source = numeric_source()
        assert client.post("/api/v1/definitions", content=source).status_code == 201
        reference = {"graph_id": "single-agent", "revision": "numeric α / source"}
        loaded = client.get("/api/v1/definitions/source", params=reference)
        assert loaded.status_code == 200 and loaded.text == source
        assert loaded.headers["cache-control"] == "no-store"
        assert client.post("/api/v1/definitions", content=loaded.text).json()["created"] is False
        assert_numeric_draft(client, reference)


def assert_numeric_draft(client: TestClient, reference: dict[str, str]) -> None:
    target = {"graph_id": "single-agent", "revision": "numeric β / variant"}
    response = client.post(
        "/api/v1/definitions/draft", json={"source": reference, "target": target}
    )
    assert response.status_code == 200
    value = json_object(decode_json(response.text))
    components = json_object(value["components"])
    parameters = json_object(
        json_object(json_object(components["proposer"])["config"])["parameters"]
    )
    assert parameters["seed"] == 9007199254740993
    assert type(parameters["temperature"]) is float and '"temperature":1.0' in response.text
    assert value["derived_from"] == reference and "view_token" not in value
    assert client.get("/api/v1/definitions/source", params=target).status_code == 404
    assert client.post("/api/v1/definitions", content=response.text).status_code == 201
    assert client.get("/api/v1/definitions/source", params=target).text == response.text
