"""Trusted preparation namespaces isolate private/run state and share only explicit resources."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import ComponentRecord, GraphRecord
from slow_thinker_ii.adapters.preparation import HostRequest, ResourceSettings, ServiceEndpoints
from slow_thinker_ii.adapters.resources import MemoryResourceAdapter
from slow_thinker_ii.application import LimitsProfile, PreparationRejected
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object
from slow_thinker_key_value_memory import KeyValueMemory
from support.preparation import SyntheticSecrets
from support.sequence_plans import graph_value
from support.workspace_data import workspace_resources


def request(runtime: str = "first", retention: str = "run") -> HostRequest:
    graph = GraphRecord.model_validate(graph_value("single-agent"))
    component = ComponentRecord(
        type_id="key-value-memory",
        type_version="0.1.0",
        config={"namespace": "same/label", "retention": retention},
        resources={},
    )
    limits = LimitsProfile("limits", 60, 10, 5, 1, 20, 5, 65536, 1000, 1000, 1000)
    return HostRequest(
        "private/a",
        component,
        graph,
        ResourceSettings.model_validate_json(encode_json(workspace_resources())),
        limits,
        ServiceEndpoints("http://127.0.0.1:8000/v1"),
        None,
        1,
        SyntheticSecrets(),
        runtime_id=runtime,
    )


def binding(adapter: MemoryResourceAdapter, selected: HostRequest) -> JsonObject:
    profile = adapter.configure(selected)
    return json_object(json_object(decode_json(profile.binding.clients_json))["memory_store"])


def test_private_shared_run_persistent_and_revision_namespaces(tmp_path: Path) -> None:
    adapter = MemoryResourceAdapter(tmp_path)
    selected = request()
    private = binding(adapter, selected)
    assert (
        private["path"] == str(tmp_path / "memory.sqlite3")
        and not tmp_path.joinpath("memory.sqlite3").exists()
    )
    assert binding(adapter, selected) == private
    assert (
        binding(adapter, replace(selected, instance_id="private/b"))["namespace"]
        != private["namespace"]
    )
    assert (
        binding(adapter, replace(selected, runtime_id="second"))["namespace"]
        != private["namespace"]
    )
    persistent = request(retention="persistent")
    original = binding(adapter, persistent)
    changed = replace(
        persistent,
        runtime_id="second",
        graph=persistent.graph.model_copy(update={"revision": "v2"}),
    )
    assert binding(adapter, changed) == original
    durable_namespaces(tmp_path, str(original["namespace"]), str(private["namespace"]))


@pytest.mark.parametrize(
    "config,code",
    [
        ({"namespace": "ns", "path": "/tmp/user"}, "invalid_memory_configuration"),
        ({"namespace": "é" * 129}, "invalid_memory_namespace"),
        ({"namespace": ""}, "invalid_memory_configuration"),
    ],
)
def test_invalid_configuration_is_rejected(tmp_path: Path, config: JsonObject, code: str) -> None:
    selected = request()
    selected = replace(selected, component=selected.component.model_copy(update={"config": config}))
    with pytest.raises(PreparationRejected) as caught:
        MemoryResourceAdapter(tmp_path).configure(selected)
    assert caught.value.code == code and not (tmp_path / "memory.sqlite3").exists()


def test_run_identity_is_required_and_tuple_encoding_avoids_collisions(tmp_path: Path) -> None:
    adapter = MemoryResourceAdapter(tmp_path)
    with pytest.raises(PreparationRejected):
        adapter.configure(request(runtime=""))
    selected = request()
    other = replace(
        selected,
        instance_id="a",
        graph=selected.graph.model_copy(update={"graph_id": "graph/private"}),
    )
    assert binding(adapter, selected)["namespace"] != binding(adapter, other)["namespace"]


def durable_namespaces(tmp_path: Path, namespace: str, private: str) -> None:
    KeyValueMemory(tmp_path / "memory.sqlite3", namespace).put({"key": "k", "value": "durable"})
    assert (
        KeyValueMemory(tmp_path / "memory.sqlite3", namespace).get({"key": "k"})["value"]
        == "durable"
    )
    assert KeyValueMemory(tmp_path / "memory.sqlite3", private).get({"key": "k"})["found"] is False
