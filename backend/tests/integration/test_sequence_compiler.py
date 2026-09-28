"""The four real JSON definitions compile against their effective instance contracts."""

from dataclasses import replace

import pytest
from slow_thinker_ii.adapters.catalog import SequenceCompiler
from slow_thinker_ii.contracts import encode_json
from slow_thinker_ii.definitions import OutputArgument, node_arguments
from support.sequence_plans import SCHEMAS, graph_value, plan, resolved


@pytest.mark.parametrize(
    "name,count", [("single-agent", 1), ("handoff", 2), ("review-cycle", 3), ("repeated-review", 5)]
)
def test_bundled_plan_preserves_every_step_and_explicit_input(name: str, count: int) -> None:
    compiled = plan(name)
    assert len(compiled.nodes) == count
    assert compiled.controller.component == "sequence"
    assert compiled.limits_profile == "illustrative-limits" and compiled.parent_json is None
    assert node_arguments(compiled.nodes[0], {}) == '{"problem":"Design a workshop"}'
    for index, node in enumerate(compiled.nodes):
        for binding in node.inputs:
            if isinstance(binding, OutputArgument):
                assert binding.node in {earlier.node_id for earlier in compiled.nodes[:index]}


def test_reused_agent_keeps_distinct_node_bindings() -> None:
    compiled = plan("review-cycle")
    outputs = {"draft": '{"value":"proposal"}', "review": '{"value":"criticism"}'}
    assert node_arguments(compiled.nodes[2], outputs) == (
        '{"problem":"Design a workshop","proposal":"proposal","review":"criticism"}'
    )
    assert compiled.nodes[0].target == compiled.nodes[2].target


@pytest.mark.parametrize("change", ["missing", "duplicate", "type", "version", "role", "operation"])
def test_resolution_must_match_the_graph(change: str) -> None:
    graph = graph_value("single-agent")
    instances = resolved(graph)
    if change == "missing":
        instances = instances[:-1]
    elif change == "duplicate":
        instances = (*instances, instances[0])
    elif change == "role":
        instances = tuple(
            replace(item, roles=()) if item.instance_id == "sequence" else item
            for item in instances
        )
    else:
        first = instances[0]
        changed = {
            "type": replace(first, type_id="unknown"),
            "version": replace(first, type_version="unknown"),
            "operation": replace(first, operations=()),
        }[change]
        instances = (changed, *instances[1:])
    with pytest.raises(ValueError):
        SequenceCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', instances)


def test_graph_cannot_silently_ignore_undeclared_core_fields() -> None:
    from jsonschema import ValidationError

    graph = graph_value("single-agent")
    graph["parallel"] = True
    with pytest.raises(ValidationError):
        SequenceCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', resolved(graph))


def test_compilation_freezes_inputs_before_external_work() -> None:
    graph = graph_value("single-agent")
    compiled = SequenceCompiler(SCHEMAS).compile(
        encode_json(graph), '{"problem":"x"}', resolved(graph)
    )
    nodes = graph["nodes"]
    assert isinstance(nodes, dict)
    nodes["extra"] = {}
    assert len(compiled.nodes) == 1 and '"extra"' not in compiled.graph_json


def test_plan_retains_variant_lineage_for_later_comparison() -> None:
    graph = graph_value("single-agent")
    graph["derived_from"] = {"graph_id": "original", "revision": "1"}
    compiled = SequenceCompiler(SCHEMAS).compile(
        encode_json(graph), '{"problem":"x"}', resolved(graph)
    )
    assert compiled.parent_json == '{"graph_id":"original","revision":"1"}'
