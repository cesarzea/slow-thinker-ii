"""Outgoing clients are supplied only to graph callers that need gateway access."""

from pathlib import Path

import pytest
from slow_thinker_ii.adapters.catalog import TypeInstallation
from slow_thinker_ii.adapters.sqlite import SqliteModelTariffReader
from slow_thinker_ii.application import PreparationRejected
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object
from support.preparation import PreparationCase
from support.sequence_plans import EXAMPLES

from models.mcp_preparation_fixture import ProfileRecorder, add_resources, resource_installations
from models.preparation_fixture import (
    Definitions,
    ModelInstallations,
    model_preparer,
    preparation_case,
)
from models.test_preparation import installed_models

__all__ = ["installed_models"]


@pytest.fixture(scope="module")
def installed_resources(installed_models: ModelInstallations) -> tuple[TypeInstallation, ...]:
    return resource_installations(installed_models.directory)


def clients(instances: JsonObject, identity: str) -> JsonObject:
    return json_object(json_object(instances[identity])["clients"])


async def test_resource_hosts_keep_exact_original_clients_without_outgoing_access(
    tmp_path: Path,
    installed_models: ModelInstallations,
    installed_resources: tuple[TypeInstallation, ...],
) -> None:
    case, definitions = await preparation_case(tmp_path, installed_models)
    add_resources(case, definitions, installed_resources)
    recorder = ProfileRecorder(case.adapters["memory"])
    case.adapters["memory"] = recorder
    workflow = await model_preparer(
        case, definitions, SqliteModelTariffReader(case.database)
    ).prepare(case.intent, "resource-runtime")
    instances = json_object(json_object(decode_json(workflow.start.snapshot_json))["instances"])
    assert clients(instances, "calculator") == {}
    assert set(clients(instances, "memory")) == {"memory_store"}
    assert clients(instances, "memory") == decode_json(
        recorder.profiles["memory"].binding.clients_json
    )
    assert set(clients(instances, "model")) == {"provider"}
    assert all(
        not workflow.policy.discover(identity) for identity in ("calculator", "memory", "model")
    )
    assert workflow.environment.report() == "[]" and not (tmp_path / "runtime").exists()


async def test_legacy_clients_and_grants_without_slots_keep_gateway_access(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case = PreparationCase(tmp_path, installed_models.directory, installed_models.selected)
    source = json_object(decode_json((EXAMPLES / "single-agent.graph.json").read_text()))
    permissions = source["permissions"]
    assert isinstance(permissions, list)
    permissions.append({"caller": "sequence", "target": "model", "operations": ["complete"]})
    recorder = ProfileRecorder(case.adapters["openai-client"])
    case.adapters["openai-client"] = recorder
    workflow = await model_preparer(case, Definitions(encode_json(source)), None).prepare(
        case.intent, "legacy-runtime"
    )
    instances = json_object(json_object(decode_json(workflow.start.snapshot_json))["instances"])
    assert set(clients(instances, "model")) == {"provider"}
    caller = clients(instances, "proposer")
    assert (
        caller["openai"]
        == json_object(decode_json(recorder.profiles["proposer"].binding.clients_json))["openai"]
    )
    assert json_object(json_object(caller["mcp"])["resources"])["model"]
    assert json_object(json_object(source["components"])["sequence"])["resources"] == {}
    assert workflow.policy.discover("sequence")
    assert set(clients(instances, "sequence")) == {"mcp"}
    assert json_object(clients(instances, "sequence")["mcp"])["resources"] == {}


async def test_configured_slots_still_require_explicit_invocation_permission(
    tmp_path: Path, installed_models: ModelInstallations
) -> None:
    case = PreparationCase(tmp_path, installed_models.directory, installed_models.selected)
    source = json_object(decode_json((EXAMPLES / "single-agent.graph.json").read_text()))
    source["permissions"] = []
    with pytest.raises(PreparationRejected, match="invalid_graph_or_resource_configuration"):
        await model_preparer(case, Definitions(encode_json(source)), None).prepare(
            case.intent, "ungranted-runtime"
        )
