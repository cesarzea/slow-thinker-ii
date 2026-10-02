"""Resource hosts reject malformed inputs and keep storage failures explicit."""

import sqlite3
from contextlib import closing
from pathlib import Path

import pytest
from mcp.shared.exceptions import MCPError
from slow_thinker_host import Invocation, JsonObject, json_object
from slow_thinker_key_value_memory import KeyValueMemory, KeyValueMemoryHost

from tooling.tests.test_external_entry_support import invalid_argv, invoke_entry

CONFIG: JsonObject = {"namespace": "human", "retention": "persistent"}


async def test_host_operations_and_storage_failure(tmp_path: Path) -> None:
    declared = KeyValueMemoryHost.describe(CONFIG)
    host = KeyValueMemoryHost(CONFIG, declared, tmp_path / "memory.sqlite3", "effective")
    assert host.operations() == declared and not (tmp_path / "memory.sqlite3").exists()
    assert (await host.invoke("put", {"key": "k", "value": 1}, Invocation("g"))).value == {
        "version": 1
    }
    cases: list[tuple[str, JsonObject]] = [("unknown", {}), ("get", {})]
    for name, arguments in cases:
        with pytest.raises(MCPError):
            await host.invoke(name, json_object(arguments), Invocation("g"))
    broken = KeyValueMemoryHost(CONFIG, declared, tmp_path, "effective")
    with pytest.raises(MCPError) as caught:
        await broken.invoke("get", {"key": "k"}, Invocation("g"))
    assert caught.value.data["reason"] == "Memory storage unavailable"
    with pytest.raises(ValueError):
        KeyValueMemoryHost(CONFIG, (), tmp_path, "effective")


@pytest.mark.parametrize(
    "field,value",
    [
        ("max_entries", True),
        ("namespace", "é" * 129),
        ("retention", "forever"),
        ("max_value_bytes", 65537),
    ],
)
def test_invalid_host_config(field: str, value: str | int) -> None:
    with pytest.raises(ValueError):
        KeyValueMemoryHost.describe({**CONFIG, field: value})


@pytest.mark.parametrize(
    "clients",
    [
        {},
        {"memory_store": {"path": "relative", "namespace": "ns"}},
        {"memory_store": {"path": 1, "namespace": "ns"}},
        {"memory_store": {"path": "/tmp/m", "namespace": ""}},
    ],
)
def test_invalid_bootstrap(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, clients: JsonObject
) -> None:
    with pytest.raises(ValueError):
        invoke_entry(
            "slow_thinker_key_value_memory",
            CONFIG,
            KeyValueMemoryHost.describe(CONFIG),
            clients,
            tmp_path,
            monkeypatch,
        )


def test_memory_main_has_no_business_io(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    invalid_argv("slow_thinker_key_value_memory", monkeypatch)
    path = tmp_path / "memory.sqlite3"
    assert invoke_entry(
        "slow_thinker_key_value_memory",
        CONFIG,
        KeyValueMemoryHost.describe(CONFIG),
        {"memory_store": {"path": str(path), "namespace": "ns"}},
        tmp_path,
        monkeypatch,
    ) == ["key-value-memory"]
    assert not path.exists()


@pytest.mark.parametrize("column,value", [("value_json", b"bad"), ("version", 0)])
def test_corrupt_durable_row_is_rejected(tmp_path: Path, column: str, value: bytes | int) -> None:
    path = tmp_path / "memory.sqlite3"
    memory = KeyValueMemory(path, "ns")
    memory.put({"key": "k", "value": 1})
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute(f"UPDATE memory_entries SET {column}=?", (value,))
    with pytest.raises(ValueError, match="durable memory"):
        memory.get({"key": "k"})
    if column == "version":
        with pytest.raises(ValueError, match="durable memory key"):
            memory.list({})


def test_exhausted_version_counter_rolls_back(tmp_path: Path) -> None:
    path = tmp_path / "memory.sqlite3"
    memory = KeyValueMemory(path, "ns")
    memory.put({"key": "k", "value": 1})
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute("UPDATE memory_versions SET version=?", (2**63 - 1,))
    with pytest.raises(ValueError, match="counter is exhausted"):
        memory.put({"key": "k", "value": 2})
    assert memory.get({"key": "k"})["value"] == 1
