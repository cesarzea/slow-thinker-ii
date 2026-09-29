"""Conditional graphs reject ambiguous feedback and invalid topology before admission."""

import pytest
from jsonschema import ValidationError
from slow_thinker_ii.adapters.catalog import ConditionalCompiler
from slow_thinker_ii.contracts import encode_json
from slow_thinker_ii.definitions import read_pointer
from support.sequence_plans import SCHEMAS, graph_value, resolved


@pytest.mark.parametrize(
    "fault", ["route", "entry", "activation", "result", "parent", "cycle", "constant"]
)
def test_invalid_conditional_graphs(fault: str) -> None:
    graph = graph_value("bounded-review")
    paths = {
        "route": ("/components/flow/config/routes/review", "revise", "absent"),
        "entry": ("/components/flow/config", "entry", "absent"),
        "result": ("/result", "missing", "omit"),
        "parent": ("/components/review-worker", "contained_by", "absent"),
        "cycle": ("/components/reviewer", "contained_by", "review-worker"),
        "constant": ("/nodes/propose/output", "constant", "absent"),
    }
    if fault == "activation":
        binding = read_pointer(graph, "/nodes/propose/inputs/proposal")
        assert isinstance(binding, dict)
        binding.pop("activation")
    else:
        pointer, key, value = paths[fault]
        target = read_pointer(graph, pointer)
        assert isinstance(target, dict)
        target[key] = value
    with pytest.raises((ValueError, ValidationError)):
        ConditionalCompiler(SCHEMAS).compile(encode_json(graph), '{"problem":"x"}', resolved(graph))
