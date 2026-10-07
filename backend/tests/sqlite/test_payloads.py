"""The recording contract's bound: oversized payload-like fields are stored as a preview."""

import json
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteRunStore
from slow_thinker_ii.contracts import JsonObject, JsonValue

from .stores import initialized, observed, starting, with_graph

FIELDS = ("payload", "input", "arguments", "result", "request", "response", "content")
USAGE: JsonObject = {"input": 10, "cached_input": 0, "cache_write": 0, "output": 5}


def store_of(directory: Path, max_payload_bytes: int | None = None) -> SqliteRunStore:
    database: SqliteDatabase = with_graph(initialized(directory))
    if max_payload_bytes is None:
        store = SqliteRunStore(database)
    else:
        store = SqliteRunStore(database, max_payload_bytes=max_payload_bytes)
    store.create(starting("r1"))
    return store


def recorded(store: SqliteRunStore, data: JsonObject) -> JsonObject:
    """The stored data, checked to equal what `append` returned."""
    event = store.append("r1", observed("component.called", data))
    assert store.events("r1", event.seq - 1, 1) == (event,)
    return event.data


@pytest.mark.parametrize("field", FIELDS)
def test_each_payload_like_field_is_bounded(tmp_path: Path, field: str) -> None:
    store = store_of(tmp_path, 64)
    small, large = "x" * 62, "y" * 63  # 64 and 65 bytes once serialized with quotes
    assert recorded(store, {field: small}) == {field: small}
    preview = f'"{large}"'  # the whole serialization, shorter than the 4 KiB preview
    assert recorded(store, {field: large}) == {
        field: {"truncated": True, "bytes": 65, "preview": preview}
    }


def test_the_default_bound_is_256_kib(tmp_path: Path) -> None:
    store = store_of(tmp_path)
    kept, cut = "k" * 262_142, "c" * 262_143
    assert recorded(store, {"payload": kept}) == {"payload": kept}
    bounded = recorded(store, {"payload": cut})["payload"]
    assert bounded == {"truncated": True, "bytes": 262_145, "preview": '"' + "c" * 4095}


def test_amounts_usage_and_other_fields_are_never_bounded(tmp_path: Path) -> None:
    store = store_of(tmp_path, 64)
    long = "z" * 500
    data: JsonObject = {
        "call_id": "c1",
        "request": {"messages": [{"role": "user", "content": long}]},
        "response": {"choices": [{"message": {"content": long}}]},
        "usage": USAGE,
        "reserved_usd": "0.000100000",
        "cost_usd": "0.000004000",
        "rates": {"input": "0.15", "output": "0.6"},
        "detail": long,
        "error": {"code": "provider_error", "message": long},
    }
    stored = recorded(store, data)
    for field in ("request", "response"):
        encoded = _encoded(data[field])
        preview = encoded[:4096].decode()
        assert stored[field] == {"truncated": True, "bytes": len(encoded), "preview": preview}
    assert {key: item for key, item in stored.items() if key not in ("request", "response")} == {
        key: item for key, item in data.items() if key not in ("request", "response")
    }


def test_previews_do_not_split_characters(tmp_path: Path) -> None:
    store = store_of(tmp_path, 64)
    text = "a" + "€" * 2000  # "€" has three bytes: the 4096-byte cut falls inside one
    bounded = recorded(store, {"content": text})["content"]
    assert isinstance(bounded, dict)
    preview = bounded["preview"]
    assert isinstance(preview, str) and preview == '"a' + "€" * 1364
    assert bounded["bytes"] == 6003


def _encoded(value: JsonValue) -> bytes:
    """The serialization the bound applies to: compact JSON in UTF-8, keys in their order."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
