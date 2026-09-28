"""Preparation freezes reproducible evidence without starting inference or retaining credentials."""

import shutil
from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import BundledDefinitionStore
from slow_thinker_ii.adapters.preparation import HostProfile, HostRequest, PlainHostAdapter
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.preparation import NOW, PreparationCase
from support.sequence_plans import EXAMPLES, graph_value


async def test_effective_snapshot_is_private_and_does_not_launch(case: PreparationCase) -> None:
    workflow = await case.preparer().prepare(case.intent, "runtime")
    record = workflow.start.record_json()
    snapshot = json_object(decode_json(workflow.start.snapshot_json))
    instances = json_object(snapshot["instances"])
    model = json_object(instances["model"])
    assert json_object(model["config"])["model"] == "gpt-6-luna"
    assert model["credentials"] == "withheld"
    assert json_object(instances["proposer"])["credentials"] == "none"
    assert "synthetic-preparation-key" not in record
    assert case.secrets.requested == ["test-provider"]
    assert workflow.environment.report() == "[]"
    assert not (case.directory / "runtime").exists()
    assert workflow.start.admit_before == NOW + 3510
    assert workflow.models[0].target.instance == "model"
    assert len(json_object(snapshot["installations"])) == 3
    assert "files_sha256" in record and "record_sha256" in record
    assert '"files":' not in record


@pytest.mark.parametrize("name", ["single-agent", "handoff", "review-cycle", "repeated-review"])
async def test_all_bundled_graphs_prepare(case: PreparationCase, name: str) -> None:
    intent = replace(case.intent, graph_id=str(graph_value(name)["graph_id"]))
    workflow = await case.preparer().prepare(intent, "runtime")
    assert workflow.start.intent == intent
    assert workflow.models


async def test_renamed_shared_resource_uses_graph_identity(
    case: PreparationCase, tmp_path: Path
) -> None:
    directory = tmp_path / "definitions"
    shutil.copytree(EXAMPLES, directory)
    path = directory / "single-agent.graph.json"
    path.write_text(
        path.read_text()
        .replace('"model": "model"', '"model": "shared-model"')
        .replace('"model": {', '"shared-model": {')
        .replace('"target": "model"', '"target": "shared-model"')
    )
    case.definitions = BundledDefinitionStore(directory)
    workflow = await case.preparer().prepare(case.intent, "runtime")
    assert workflow.models[0].target.instance == "shared-model"
    assert '"shared-model"' in workflow.start.snapshot_json


class RecordingAdapter:
    def __init__(self) -> None:
        self.instances: list[str] = []

    def configure(self, request: HostRequest) -> HostProfile:
        self.instances.append(request.instance_id)
        return PlainHostAdapter().configure(request)


async def test_registered_adapter_receives_component_context(case: PreparationCase) -> None:
    adapter = RecordingAdapter()
    case.adapters["mcp"] = adapter
    workflow = await case.preparer().prepare(case.intent, "runtime")
    assert adapter.instances == ["sequence"]
    assert workflow.start.runtime_id == "runtime"


async def test_snapshot_size_is_checked_before_environment_creation(case: PreparationCase) -> None:
    assert case.configuration is not None
    case.configuration = replace(
        case.configuration, limits=replace(case.configuration.limits, max_payload_bytes=100)
    )
    with pytest.raises(PreparationRejected, match="snapshot_limit"):
        await case.preparer().prepare(case.intent, "runtime")
    assert not (case.directory / "runtime").exists()


async def test_snapshot_retains_original_and_effective_configs(case: PreparationCase) -> None:
    workflow = await case.preparer().prepare(case.intent, "runtime")
    snapshot = json_object(decode_json(workflow.start.snapshot_json))
    definition = json_object(snapshot["definition"])
    original = json_object(json_object(definition["components"])["model"])["config"]
    effective = json_object(json_object(snapshot["instances"])["model"])["config"]
    assert original != effective
    assert encode_json(original).find("provider_profile") >= 0
