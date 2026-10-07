"""The bootstrap document is read once, exactly as `slow-thinker.bootstrap/1` defines it."""

import json
from pathlib import Path

import pytest
from slow_thinker_host import Bootstrap, JsonObject, JsonValue, Position, read_bootstrap

DOCUMENT: JsonObject = {
    "format": "slow-thinker.bootstrap/1",
    "component": "llm-call@1.0.0",
    "node": {"id": "proposer", "name": "Proposer"},
    "position": "node",
    "config": {"prompt": "Be funny.", "model": None},
    "platform": {
        "llm_base_url": "http://127.0.0.1:8000/v1",
        "mcp_url": "https://platform.example:8443/mcp",
    },
    "limits": {"max_concurrent_invocations": 4},
}


def write(tmp_path: Path, document: object) -> Path:
    path = tmp_path / "bootstrap.json"
    path.write_text(json.dumps(document), encoding="utf-8")
    return path


@pytest.mark.parametrize("position", ["node", "output", "memory"])
def test_bootstrap_document_is_read_into_its_fields(tmp_path: Path, position: Position) -> None:
    loaded = read_bootstrap(write(tmp_path, {**DOCUMENT, "position": position}))
    assert loaded == Bootstrap(
        component="llm-call@1.0.0",
        node_id="proposer",
        node_name="Proposer",
        position=position,
        config={"prompt": "Be funny.", "model": None},
        llm_base_url="http://127.0.0.1:8000/v1",
        mcp_url="https://platform.example:8443/mcp",
        max_concurrent_invocations=4,
    )


def changed(field: str, value: JsonValue) -> JsonObject:
    return {**DOCUMENT, field: value}


INVALID: list[JsonObject] = [
    {key: value for key, value in DOCUMENT.items() if key != "limits"},
    {**DOCUMENT, "extra": True},
    changed("format", "slow-thinker.bootstrap/2"),
    changed("component", "llm-call"),
    changed("component", "LLM@1.0.0"),
    changed("component", 7),
    changed("node", {"id": "proposer"}),
    changed("node", {"id": "", "name": "Proposer"}),
    changed("position", "embedded"),
    changed("config", []),
    changed("platform", {"llm_base_url": "http://127.0.0.1:8000/v1"}),
    changed("platform", {"llm_base_url": "ftp://host/v1", "mcp_url": "http://h/mcp"}),
    changed("platform", {"llm_base_url": "http:///v1", "mcp_url": "http://h/mcp"}),
    changed("platform", {"llm_base_url": "http://user:key@h/v1", "mcp_url": "http://h/mcp"}),
    changed("platform", {"llm_base_url": "http://h/v1?key=1", "mcp_url": "http://h/mcp"}),
    changed("platform", {"llm_base_url": "http://h:0/v1", "mcp_url": "http://h/mcp"}),
    changed("platform", {"llm_base_url": "http://h:port/v1", "mcp_url": "http://h/mcp"}),
    changed("limits", {"max_concurrent_invocations": 0}),
    changed("limits", {"max_concurrent_invocations": True}),
    changed("limits", {"max_concurrent_invocations": 2.5}),
]


@pytest.mark.parametrize("document", INVALID)
def test_invalid_bootstrap_documents_are_rejected(tmp_path: Path, document: JsonObject) -> None:
    with pytest.raises(ValueError):
        read_bootstrap(write(tmp_path, document))


@pytest.mark.parametrize("text", ["[]", '{"format": 1, "format": 2}', "not json"])
def test_bootstrap_must_be_one_json_object(tmp_path: Path, text: str) -> None:
    path = tmp_path / "bootstrap.json"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError):
        read_bootstrap(path)
