"""Durable state, version preconditions, bounded data and namespace separation."""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from slow_thinker_host import JsonObject, json_object
from slow_thinker_key_value_memory import KeyValueMemory


def test_lazy_state_restart_namespaces_and_aba(tmp_path: Path) -> None:
    path = tmp_path / "nested/memory.sqlite3"
    memory = KeyValueMemory(path, "private")
    assert not path.exists()
    assert memory.get({"key": "a"}) == {"found": False, "value": None, "version": None}
    inserted = memory.put(
        {"key": "a", "value": {"large": 9007199254740993}, "expected_version": None}
    )
    assert inserted == {"version": 1}
    restarted = KeyValueMemory(path, "private")
    assert restarted.get({"key": "a"})["value"] == {"large": 9007199254740993}
    assert KeyValueMemory(path, "other").get({"key": "a"})["found"] is False
    deleted = memory.delete({"key": "a", "expected_version": 1})
    assert deleted == {"deleted": True}
    replaced = restarted.put({"key": "a", "value": None})
    assert replaced == {"version": 2}
    with pytest.raises(ValueError, match="version_conflict"):
        memory.put({"key": "a", "value": "stale", "expected_version": 1})
    assert restarted.get({"key": "a"})["version"] == 2
    missing = memory.delete({"key": "absent"})
    assert missing == {"deleted": False}
    assert path.exists()


@pytest.mark.parametrize(
    "operation,arguments",
    [
        ("get", {}),
        ("get", {"key": "a", "extra": 1}),
        ("get", {"key": ""}),
        ("get", {"key": "é" * 129}),
        ("put", {"key": "a"}),
        ("put", {"key": "a", "value": 1, "expected_version": False}),
        ("put", {"key": "a", "value": 1, "expected_version": 0}),
        ("delete", {"key": "a", "expected_version": "1"}),
        ("list", {"limit": 101}),
        ("list", {"limit": True}),
        ("list", {"after": ""}),
    ],
)
def test_invalid_requests_are_rejected_without_writes(
    tmp_path: Path, operation: str, arguments: JsonObject
) -> None:
    memory = KeyValueMemory(tmp_path / "memory.sqlite3", "ns")
    methods = {"get": memory.get, "put": memory.put, "delete": memory.delete, "list": memory.list}
    with pytest.raises(ValueError):
        methods[operation](arguments)
    assert not (tmp_path / "memory.sqlite3").exists()


def test_capacity_bytes_paging_and_conflicts_preserve_data(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    memory = KeyValueMemory(path, "ns", max_entries=2, max_value_bytes=6)
    first = memory.put({"key": "b", "value": "é"})
    assert first == {"version": 1}
    second = memory.put({"key": "a", "value": 1})
    assert second == {"version": 2}
    for arguments in [
        {"key": "c", "value": 3},
        {"key": "a", "value": "ééé"},
        {"key": "b", "value": 4, "expected_version": None},
    ]:
        with pytest.raises(ValueError):
            memory.put(json_object(arguments))
    assert memory.list({"limit": 1}) == {"items": [{"key": "a", "version": 2}], "next_key": "a"}
    assert memory.list({"after": "a"}) == {"items": [{"key": "b", "version": 1}], "next_key": None}
    updated = memory.put({"key": "a", "value": 4, "expected_version": 2})
    assert updated == {"version": 3}
    with pytest.raises(ValueError, match="version_conflict"):
        memory.delete({"key": "a", "expected_version": None})
    with pytest.raises(ValueError, match="configured bound"):
        KeyValueMemory(path, "ns", max_value_bytes=1).get({"key": "b"})
    assert memory.get({"key": "a"})["value"] == 4


def test_concurrent_compare_and_swap_has_one_winner(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    memory = KeyValueMemory(path, "shared")
    memory.put({"key": "k", "value": 0})

    def update(value: int) -> bool:
        try:
            KeyValueMemory(path, "shared").put({"key": "k", "value": value, "expected_version": 1})
            return True
        except ValueError:
            return False

    with ThreadPoolExecutor(max_workers=4) as workers:
        outcomes = tuple(workers.map(update, range(4)))
    assert sum(outcomes) == 1
    assert memory.get({"key": "k"})["version"] == 2


@pytest.mark.parametrize("namespace,entries,bytes_", [("", 1, 1), ("ns", 0, 1), ("ns", 1, 65537)])
def test_invalid_constructor_limits(
    tmp_path: Path, namespace: str, entries: int, bytes_: int
) -> None:
    with pytest.raises(ValueError):
        KeyValueMemory(tmp_path / "m", namespace, max_entries=entries, max_value_bytes=bytes_)
