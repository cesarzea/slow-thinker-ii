"""Repeated bindings identify exact successful activations, never merely participants."""

from dataclasses import replace

import pytest
from slow_thinker_ii.definitions import (
    CompletedActivation,
    LatestOutput,
    conditional_arguments,
    selected_port,
)
from slow_thinker_ii.execution import ActivationLimitReached, require_conditional_decision
from support.conditional import conditional_plan


def test_optional_initial_feedback_is_omitted() -> None:
    node = conditional_plan().nodes[0]
    assert conditional_arguments(node, ()).arguments_json == '{"problem":"accept"}'


def test_latest_reference_keeps_source_and_rejects_missing_pointer() -> None:
    node = conditional_plan().nodes[0]
    history = (
        CompletedActivation("propose", "one", "response:one", '{"value":"old"}', "next"),
        CompletedActivation("propose", "two", "response:two", '{"value":"new"}', "next"),
    )
    result = conditional_arguments(node, history)
    assert (
        '"proposal":"new"' in result.arguments_json
        and '"activation_id":"two"' in result.sources_json
    )
    node = replace(node, inputs=(LatestOutput("input", "propose", "/missing", True),))
    with pytest.raises(ValueError):
        conditional_arguments(node, history)


@pytest.mark.parametrize("reply", ["{}", '{"port":3}', '{"port":"unknown"}'])
def test_unknown_selected_ports_fail(reply: str) -> None:
    with pytest.raises(ValueError):
        selected_port(conditional_plan().nodes[1], reply)


def test_terminal_route_precedes_exhaustion_and_bad_decisions_fail() -> None:
    require_conditional_decision({"action": "complete"}, None, 6, 6)
    with pytest.raises(ActivationLimitReached):
        require_conditional_decision(
            {"action": "exhausted", "reason": "activation_limit_reached"}, "next", 6, 6
        )
    with pytest.raises(ValueError):
        require_conditional_decision({"action": "activate", "nodes": ["wrong"]}, "next", 0, 6)
