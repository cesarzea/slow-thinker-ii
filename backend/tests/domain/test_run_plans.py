"""Run plans compiled from valid documents: nodes, kinds, ports, routes, limits and selections."""

from typing import cast

import pytest
from slow_thinker_ii.catalog import OUTPUT, TRIGGER, ComponentRef, parse_declaration
from slow_thinker_ii.graphs import GraphInvalid, Limits, PlanNode, RunPlan, compile_plan

from .contract_fixtures import (
    J1,
    J2,
    J3,
    changed,
    declaration_example,
    graph_example,
    step_one_catalog,
)


def plan_of(name: str, version: int = 1) -> RunPlan:
    return compile_plan(graph_example(name), step_one_catalog(), version)


def test_plan_identity_and_limits() -> None:
    plan = plan_of(J1, 4)
    assert (plan.graph_id, plan.version, plan.name) == (J1, 4, "Funny story")
    assert plan.trigger_id == "story"
    assert plan.limits == Limits(20, 4, 300, 100_000_000)
    assert plan.limits.budget_nanos == 100_000_000
    assert (plan.limits.max_activations, plan.limits.max_running_nodes) == (20, 4)
    assert plan.limits.time_limit_seconds == 300


def test_plan_nodes_in_document_order() -> None:
    plan = plan_of(J1)
    assert list(plan.nodes) == ["story", "proposer", "result"]
    story, proposer, result = plan.nodes.values()
    assert (story.kind, story.inputs, story.outputs) == ("trigger", (), ("out",))
    assert (result.kind, result.inputs, result.outputs) == ("output", ("in",), ())
    assert (story.host.declaration.ref, result.host.declaration.ref) == (TRIGGER, OUTPUT)
    assert (proposer.id, proposer.name, proposer.kind) == ("proposer", "Proposer", "package")
    assert proposer.host.llm_entries == frozenset({"openai/gpt-6-luna"})
    assert proposer.embedded_output is None
    assert not any(node.stateful for node in plan.nodes.values())
    assert plan.node("proposer") is proposer
    assert plan.routes == {
        ("story", "out"): (("proposer", "in"),),
        ("proposer", "out"): (("result", "in"),),
    }


def test_an_embedded_router_provides_the_node_outputs() -> None:
    plan = plan_of(J2)
    judge = plan.node("judge")
    assert judge.outputs == ("funny", "not_funny")
    assert judge.host.llm_entries == frozenset({"deepseek/deepseek-flash"})
    embedded = judge.embedded_output
    assert embedded is not None
    assert embedded.declaration.ref == ComponentRef("router", "1.0.0")
    assert embedded.config["outputs"] == ["funny", "not_funny"]
    assert embedded.llm_entries == frozenset()
    assert plan.routes[("judge", "funny")] == (("funny", "in"),)
    assert ("judge", "out") not in plan.routes


def test_routes_list_targets_in_document_order() -> None:
    document = graph_example(J3)
    connections = document["connections"]
    assert isinstance(connections, list)
    connections.append({"from": "story.out", "to": "reviewer.in"})
    plan = compile_plan(document, step_one_catalog(), 1)
    assert plan.routes[("story", "out")] == (("proposer", "in"), ("reviewer", "in"))
    assert plan.routes[("reviewer", "revise")] == (("proposer", "in"),)


def test_stateful_components_make_their_node_stateful() -> None:
    stateful = changed(declaration_example("router"), ("state",), "stateful")
    stateful = parse_declaration(changed(stateful, ("version",), "2.0.0"))
    path = ("nodes", 1, "embedded", 0, "component")
    document = changed(graph_example(J2), path, "router@2.0.0")
    plan = compile_plan(document, step_one_catalog(stateful), 1)
    assert plan.node("judge").stateful is True
    assert plan.node("story").stateful is False


def test_plans_are_independent_of_the_source_document() -> None:
    document = graph_example(J1)
    plan = compile_plan(document, step_one_catalog(), 1)
    nodes = document["nodes"]
    assert isinstance(nodes, list) and isinstance(nodes[1], dict)
    nodes[1]["config"] = {}
    assert plan.node("proposer").host.config["prompt"] != ""
    with pytest.raises(TypeError):
        cast(dict[str, PlanNode], plan.nodes)["extra"] = plan.node("story")
    with pytest.raises(KeyError):
        plan.node("ghost")


def test_invalid_documents_are_refused_with_all_diagnostics() -> None:
    document = changed(graph_example(J1), ("limits", "budget_usd"), "0")
    document = changed(document, ("layout", "ghost"), [0, 0])
    with pytest.raises(GraphInvalid) as raised:
        compile_plan(document, step_one_catalog(), 1)
    codes = [item.code for item in raised.value.diagnostics]
    assert codes == ["unknown_layout_node", "invalid_limits"]
    assert (
        str(raised.value) == "The graph has 1 error(s): Budget per run must be greater than zero."
    )
