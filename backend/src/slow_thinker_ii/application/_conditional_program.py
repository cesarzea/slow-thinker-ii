"""Execute one bounded activation at a time, retaining feedback identity and decisions."""

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.contracts import JsonValue, decode_json, encode_json, json_object
from slow_thinker_ii.definitions import (
    CompletedActivation,
    ConditionalNode,
    ConditionalPlan,
    conditional_arguments,
    latest_output,
    read_pointer,
    selected_port,
)
from slow_thinker_ii.execution import require_conditional_decision

from ._call_runner import ManagedCalls
from ._dispatch_ports import ManagedResult


class ConditionalProgram:
    def __init__(self, plan: ConditionalPlan) -> None:
        self._plan = plan

    async def execute(self, calls: ManagedCalls) -> str:
        history: tuple[CompletedActivation, ...] = ()
        expected: str | None = self._plan.entry
        nodes = {node.node_id: node for node in self._plan.nodes}
        while True:
            await self._decide(calls, history, expected)
            if expected is None:
                return self._result(history)
            node = nodes[expected]
            completed = await self._activate(calls, node, history)
            history += (completed,)
            expected = dict(node.routes)[completed.port]

    async def _activate(
        self, calls: ManagedCalls, node: ConditionalNode, history: tuple[CompletedActivation, ...]
    ) -> CompletedActivation:
        bound = conditional_arguments(node, history)
        result = await calls.schedule(
            OperationAddress(node.target.component, node.target.operation),
            bound.arguments_json,
            node_id=node.node_id,
            sources_json=bound.sources_json,
        )
        return self._completed(calls, node, result, len(history) + 1)

    def _completed(
        self, calls: ManagedCalls, node: ConditionalNode, result: ManagedResult, ordinal: int
    ) -> CompletedActivation:
        if not result.outcome.publish or result.result.is_error:
            raise ValueError("Unsuccessful activations cannot select a route")
        port = selected_port(node, result.result.payload_json)
        activation = result.context.activation_id
        if activation is None:
            raise ValueError("A scheduled conditional node requires activation identity")
        calls.record(
            result.context,
            "activation.routed",
            {
                "activation_id": activation,
                "node": node.node_id,
                "ordinal": ordinal,
                "selected_port": port,
                "payload_id": "response:" + result.receipt_id,
            },
        )
        return CompletedActivation(
            node.node_id,
            activation,
            "response:" + result.receipt_id,
            result.result.payload_json,
            port,
        )

    async def _decide(
        self, calls: ManagedCalls, history: tuple[CompletedActivation, ...], expected: str | None
    ) -> None:
        completed: list[JsonValue] = [{"node": item.node, "port": item.port} for item in history]
        controller = self._plan.controller
        result = await calls.schedule(
            OperationAddress(controller.component, controller.operation),
            encode_json({"completed": completed}),
            activation=False,
        )
        if not result.outcome.publish or result.result.is_error:
            raise ValueError("Controller failed to produce an eligible decision")
        decision = json_object(decode_json(result.result.payload_json))
        calls.record(
            result.context,
            "controller.decided",
            {
                "decision": decision,
                "completed_activations": [item.activation_id for item in history],
            },
        )
        require_conditional_decision(decision, expected, len(history), self._plan.max_activations)

    def _result(self, history: tuple[CompletedActivation, ...]) -> str:
        source = latest_output(self._plan.result, history)
        if source is None:
            raise ValueError("Final conditional result is unavailable")
        return encode_json(
            {
                "status": "accepted",
                "value": read_pointer(decode_json(source.output_json), self._plan.result.pointer),
                "source_activation": source.activation_id,
                "activation_count": len(history),
            }
        )
