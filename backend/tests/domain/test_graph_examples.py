"""The validated journeys are valid documents; a new LLM Call names what it still needs."""

import pytest
from slow_thinker_ii.catalog import parse_declaration
from slow_thinker_ii.graphs import Diagnostic, compile_plan, has_errors

from .contract_fixtures import (
    J1,
    J2,
    J3,
    changed,
    declaration_example,
    graph_example,
    step_one_catalog,
)
from .graph_checks import validate


@pytest.mark.parametrize("name", [J1, J2, J3])
def test_journey_examples_validate_and_compile(name: str) -> None:
    document = graph_example(name)
    assert validate(document) == ()
    plan = compile_plan(document, step_one_catalog(), 1)
    assert (plan.graph_id, plan.version) == (name, 1)


def test_the_review_loop_routes_revisions_back_to_the_proposer() -> None:
    plan = compile_plan(graph_example(J3), step_one_catalog(), 3)
    assert plan.routes[("reviewer", "revise")] == (("proposer", "in"),)
    assert plan.routes[("reviewer", "accepted")] == (("result", "in"),)


def test_an_llm_call_from_its_initial_configuration() -> None:
    initial = parse_declaration(declaration_example("llm-call")).initial_config
    document = changed(graph_example(J1), ("nodes", 1, "config"), initial)
    diagnostics = validate(document)
    assert [item.document() for item in diagnostics] == [
        {
            "severity": "error",
            "code": "service_not_selected",
            "message": "Select a model.",
            "path": "/nodes/1/config/model",
            "node_id": "proposer",
        },
        {
            "severity": "error",
            "code": "invalid_config",
            "message": "Instructions is required.",
            "path": "/nodes/1/config/prompt",
            "node_id": "proposer",
        },
    ]
    assert has_errors(diagnostics)


def test_warnings_are_not_errors() -> None:
    warning = Diagnostic("warning", "no_output_node", "Text.", "/nodes", None)
    error = Diagnostic("error", "trigger_count", "Text.", "/nodes", None)
    assert not has_errors([warning])
    assert not has_errors([])
    assert has_errors(iter([warning, error]))
