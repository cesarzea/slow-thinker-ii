"""Invalid references and resource authority fail before any component can be invoked."""

import pytest
from jsonschema import ValidationError
from slow_thinker_ii.adapters.catalog import SequenceCompiler
from slow_thinker_ii.contracts import JsonValue, encode_json
from slow_thinker_ii.definitions import node_arguments, read_pointer
from support.sequence_plans import SCHEMAS, graph_value, resolved


@pytest.mark.parametrize(
    "parent,key,value",
    [
        ("/nodes/draft", "component", "missing"),
        ("/nodes/draft", "operation", "missing"),
        ("/controller", "component", "missing"),
        ("/nodes/review/inputs/proposal", "node", "review"),
        ("/nodes/review/inputs/proposal", "node", "revise"),
        ("/nodes/draft/inputs/problem", "pointer", "/missing"),
        ("/components/proposer", "resources", {}),
        ("/components/proposer/resources", "model", "missing"),
        ("/components/proposer/resources", "model", "sequence"),
        ("/components/proposer/resources", "unknown", "model"),
        ("/components/sequence/config", "steps", ["draft", "review", "review"]),
        ("/components/sequence/config", "steps", ["draft"]),
        ("/nodes/draft/inputs", "problem", {"source": "literal", "value": 3}),
        ("/nodes/draft/inputs", "problem", {"source": "literal"}),
        ("", "permissions", []),
        ("", "permissions", [{"caller": "missing", "target": "model", "operations": ["complete"]}]),
        ("", "permissions", [{"caller": "proposer", "target": "model", "operations": ["missing"]}]),
    ],
)
def test_graph_rejects_invalid_references(parent: str, key: str, value: JsonValue) -> None:
    graph = graph_value("review-cycle")
    contracts = resolved(graph)
    target = read_pointer(graph, parent)
    assert isinstance(target, dict)
    target[key] = value
    with pytest.raises((ValueError, ValidationError)):
        SequenceCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', contracts)


def test_literal_null_is_distinct_from_an_absent_literal_value() -> None:
    graph = graph_value("single-agent")
    target = read_pointer(graph, "/nodes/draft/inputs/problem")
    assert isinstance(target, dict)
    target.clear()
    target.update({"source": "literal", "value": None})
    schema = read_pointer(graph, "/components/proposer/config/input_schema/properties/problem")
    assert isinstance(schema, dict)
    schema["type"] = ["string", "null"]
    compiled = SequenceCompiler(SCHEMAS).compile(encode_json(graph), "{}", resolved(graph))
    assert node_arguments(compiled.nodes[0], {}) == '{"problem":null}'
