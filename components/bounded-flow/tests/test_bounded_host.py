"""MCP decisions preserve exact wire shapes and reject malformed history records."""

import pytest
from slow_thinker_bounded_flow import BoundedFlow, BoundedFlowConfig, BoundedFlowHost, FlowRoute
from slow_thinker_host import Invocation, JsonObject, JsonValue, Operation

CONFIG: JsonObject = {
    "entry": "step",
    "routes": {"step": {"again": "step", "done": None}},
    "max_activations": 1,
}


@pytest.mark.parametrize(
    "history,expected",
    [
        ([], {"action": "activate", "nodes": ["step"]}),
        ([{"node": "step", "port": "done"}], {"action": "complete"}),
        (
            [{"node": "step", "port": "again"}],
            {"action": "exhausted", "reason": "activation_limit_reached"},
        ),
    ],
)
async def test_host_preserves_exact_decision_shapes(
    history: JsonValue, expected: JsonObject
) -> None:
    (operation,) = BoundedFlowHost.describe(CONFIG)
    host = BoundedFlowHost(CONFIG, operation)
    assert host.operations() == (operation,)
    assert (
        await host.invoke("next", {"completed": history}, Invocation("grant"))
    ).value == expected


INVALID: list[JsonObject] = [
    {},
    {"completed": {}},
    {"completed": [{}]},
    {"completed": [{"node": 1, "port": "done"}]},
]


@pytest.mark.parametrize("arguments", INVALID)
async def test_malformed_history_is_rejected(arguments: JsonObject) -> None:
    (operation,) = BoundedFlowHost.describe(CONFIG)
    with pytest.raises(ValueError):
        await BoundedFlowHost(CONFIG, operation).invoke("next", arguments, Invocation("grant"))


async def test_host_contract_and_operation_must_match() -> None:
    with pytest.raises(ValueError, match="schemas"):
        BoundedFlowHost(CONFIG, Operation("next", {}, {}))
    (operation,) = BoundedFlowHost.describe(CONFIG)
    with pytest.raises(ValueError, match="invocation"):
        await BoundedFlowHost(CONFIG, operation).invoke("wrong", {"completed": []}, Invocation("g"))


def test_direct_immutable_configuration_rejects_duplicate_routes() -> None:
    route = FlowRoute("node", "port", None)
    with pytest.raises(ValueError, match="Duplicate"):
        BoundedFlow(BoundedFlowConfig("node", (route, route), 1))
