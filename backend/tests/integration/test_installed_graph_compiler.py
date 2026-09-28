"""Graph compilation depends on actual installed descriptions and declared resource permissions."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.installed_graphs import compiler, types
from support.sequence_plans import graph_value

INPUT = '{"problem":"Design a workshop"}'


def test_graph_retains_effective_contracts_and_installation_evidence(tmp_path: Path) -> None:
    installed = compiler(tmp_path, types(tmp_path)).compile(
        encode_json(graph_value("review-cycle")), INPUT
    )
    assert len(installed.plan.nodes) == 3 and len(installed.configurations) == 4
    for config in installed.configurations:
        snapshot = json_object(decode_json(config.description.installation_json))
        assert snapshot["identity"] == config.resolution_id
        assert config.description.config_json
    proposer = next(item for item in installed.plan.instances if item.instance_id == "proposer")
    assert '"problem"' in proposer.operations[0].input_schema_json
    assert proposer.resources[0].operations == ("complete",)


@pytest.mark.parametrize(
    "fault",
    ["missing", "duplicate", "wrong_installation", "operation", "permission", "unknown_config"],
)
def test_bad_installation_selection_or_contract_blocks_the_graph(
    tmp_path: Path, fault: str
) -> None:
    selected = types(tmp_path)
    graph = graph_value("single-agent")
    overrides: dict[str, str] = {}
    if fault == "missing":
        selected = selected[:1]
    elif fault == "duplicate":
        selected = (*selected, selected[0])
    elif fault == "wrong_installation":
        selected = (replace(selected[0], resolution_id=selected[1].resolution_id), *selected[1:])
    elif fault == "operation":
        descriptor = json_object(decode_json(selected[1].descriptor_json))
        descriptor["operations"] = {"other": json_object(descriptor["operations"])["generate"]}
        selected = (
            selected[0],
            replace(selected[1], descriptor_json=encode_json(descriptor)),
            selected[2],
        )
    elif fault == "permission":
        graph["permissions"] = []
    else:
        overrides["absent"] = "{}"
    with pytest.raises(ValueError):
        compiler(tmp_path, selected).compile(encode_json(graph), INPUT, overrides)


def test_mcp_alias_is_rejected_before_graph_admission(tmp_path: Path) -> None:
    selected = list(types(tmp_path))
    descriptor = json_object(decode_json(selected[1].descriptor_json))
    operations = json_object(descriptor["operations"])
    operation = json_object(operations["generate"])
    operation["mcp_tool"] = "unavailable_alias"
    operations["generate"] = operation
    descriptor["operations"] = operations
    selected[1] = replace(selected[1], descriptor_json=encode_json(descriptor))
    with pytest.raises(ValueError, match="MCP tool names"):
        compiler(tmp_path, tuple(selected)).compile(encode_json(graph_value("single-agent")), INPUT)
