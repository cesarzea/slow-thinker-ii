"""Trigger count, run budget, warnings, and the order of diagnostics."""

import pytest
from slow_thinker_ii.contracts import JsonObject, value_at_pointer
from slow_thinker_ii.graphs import compile_plan

from .contract_fixtures import J1, appended, changed, graph_example, step_one_catalog, without
from .graph_checks import found, found_with

UNCONNECTED_STORY = "Output “out” of Story is not connected; messages sent there are discarded."


def numbered_trigger(index: int) -> JsonObject:
    return {
        "id": f"story{index}",
        "name": f"Story {index}",
        "component": "trigger@1.0.0",
        "config": {"message": "Hi"},
    }


def test_a_graph_needs_a_trigger() -> None:
    document = changed(graph_example(J1), ("nodes", 0, "component"), "output@1.0.0")
    document = changed(document, ("nodes", 0, "config"), {})
    message = "The graph needs a Trigger node."
    assert found_with(document, "trigger_count") == [("trigger_count", "/nodes", message, None)]


def test_a_graph_has_only_one_trigger() -> None:
    document = appended(graph_example(J1), ("nodes",), numbered_trigger(2))
    message = "The graph has 2 Trigger nodes; keep only one."
    assert found_with(document, "trigger_count") == [("trigger_count", "/nodes", message, None)]


@pytest.mark.parametrize("budget", ["0", "0.000000000"])
def test_the_run_budget_must_be_positive(budget: str) -> None:
    document = changed(graph_example(J1), ("limits", "budget_usd"), budget)
    message = "Budget per run must be greater than zero."
    assert found(document) == [("invalid_limits", "/limits/budget_usd", message, None)]


def test_unconnected_inputs_and_outputs_are_warnings() -> None:
    document = without(graph_example(J1), ("connections", 0))
    assert found(document) == [
        ("unconnected_output", "/nodes/0", UNCONNECTED_STORY, "story"),
        (
            "unconnected_input",
            "/nodes/1",
            "Proposer has no incoming connection and never runs.",
            "proposer",
        ),
    ]
    assert compile_plan(document, step_one_catalog(), 2).routes[("story", "out")] == ()


def test_graphs_without_an_output_node() -> None:
    document = without(without(graph_example(J1), ("connections", 1)), ("nodes", 2))
    document = without(document, ("layout", "result"))
    assert found_with(document, "no_output_node") == [
        (
            "no_output_node",
            "/nodes",
            "The graph has no Output node, so runs produce no results.",
            None,
        )
    ]


def test_layout_entries_without_a_node() -> None:
    document = changed(graph_example(J1), ("layout", "ghost~/x"), [0, 0])
    message = "The layout entry “ghost~/x” does not match a node and is ignored."
    assert found(document) == [("unknown_layout_node", "/layout/ghost~0~1x", message, None)]


def test_diagnostics_are_ordered_by_path_with_numeric_indices() -> None:
    document = graph_example(J1)
    for index in range(3, 12):
        node: JsonObject = {
            "id": f"out{index}",
            "name": f"Out {index}",
            "component": "output@1.0.0",
            "config": {},
        }
        document = appended(document, ("nodes",), node)
    assert [path for _, path, *_ in found(document)] == [f"/nodes/{i}" for i in range(3, 12)]


def test_diagnostics_at_one_path_are_ordered_by_code() -> None:
    proposer = value_at_pointer(graph_example(J1), ("nodes", 1))
    document = changed(graph_example(J1), ("nodes",), [proposer])
    document = changed(changed(document, ("connections",), []), ("layout",), {})
    assert [(path, code) for code, path, *_ in found(document)] == [
        ("/nodes", "no_output_node"),
        ("/nodes", "trigger_count"),
        ("/nodes/0", "unconnected_input"),
        ("/nodes/0", "unconnected_output"),
    ]
