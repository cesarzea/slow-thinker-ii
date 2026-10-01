"""Conditional compilation rejects wrong profiles and identities before running participants."""

from dataclasses import replace

import pytest
from slow_thinker_ii.adapters.catalog import ConditionalCompiler
from slow_thinker_ii.contracts import encode_json
from slow_thinker_ii.definitions import StaticArgument
from support.composition_installations import change_object
from support.sequence_plans import SCHEMAS, graph_value, resolved


def test_conditional_compiler_requires_the_declared_profile() -> None:
    graph = graph_value("single-agent")
    with pytest.raises(ValueError, match="declared profile"):
        ConditionalCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', resolved(graph))


def test_controller_must_resolve_to_control_role() -> None:
    graph = graph_value("bounded-review")
    instances = tuple(
        replace(item, roles=("agent",)) if item.instance_id == "flow" else item
        for item in resolved(graph)
    )
    with pytest.raises(ValueError, match="control role"):
        ConditionalCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', instances)


@pytest.mark.parametrize(
    "pointer,reason",
    [("/result", "Final output"), ("/nodes/propose/inputs/proposal", "reference declared nodes")],
)
def test_completed_references_require_a_declared_node(pointer: str, reason: str) -> None:
    graph = graph_value("bounded-review")
    change_object(graph, pointer)["node"] = "absent"
    with pytest.raises(ValueError, match=reason):
        ConditionalCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', resolved(graph))


def test_literal_only_inputs_are_validated_and_frozen() -> None:
    graph = graph_value("bounded-review")
    change_object(graph, "/nodes/propose")["inputs"] = {
        "problem": {"source": "literal", "value": "fixed"}
    }
    plan = ConditionalCompiler(SCHEMAS).compile(
        encode_json(graph), '{"problem":"x"}', resolved(graph)
    )
    assert plan.nodes[0].inputs == (StaticArgument("problem", '"fixed"'),)
