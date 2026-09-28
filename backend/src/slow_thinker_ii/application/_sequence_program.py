"""Execute admitted graph data through its controller and the ordinary managed-call path."""

from slow_thinker_ii.access import AccessPolicy, OperationAddress, Permission
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object
from slow_thinker_ii.definitions import SequencePlan, node_arguments
from slow_thinker_ii.execution import require_sequence_decision

from ._call_runner import ManagedCalls


class SequenceProgram:
    def __init__(self, plan: SequencePlan) -> None:
        self._plan = plan

    async def execute(self, calls: ManagedCalls) -> str:
        outputs: dict[str, str] = {}
        for node in self._plan.nodes:
            await self._decide(calls, tuple(outputs), node.node_id)
            target = OperationAddress(node.target.component, node.target.operation)
            result = await calls.schedule(
                target, node_arguments(node, outputs), node_id=node.node_id
            )
            if not result.outcome.publish or result.result.is_error:
                raise ValueError("Unsuccessful node results cannot advance the graph")
            json_object(decode_json(result.result.payload_json))
            outputs[node.node_id] = result.result.payload_json
        await self._decide(calls, tuple(outputs), None)
        values: JsonObject = {name: decode_json(value) for name, value in outputs.items()}
        return encode_json({"nodes": values})

    async def _decide(
        self, calls: ManagedCalls, completed: tuple[str, ...], expected: str | None
    ) -> None:
        controller = self._plan.controller
        arguments: JsonObject = {"completed_nodes": list(completed)}
        result = await calls.schedule(
            OperationAddress(controller.component, controller.operation),
            encode_json(arguments),
            activation=False,
        )
        if not result.outcome.publish or result.result.is_error:
            raise ValueError("Controller call did not produce an eligible decision")
        require_sequence_decision(json_object(decode_json(result.result.payload_json)), expected)


def sequence_access(plan: SequencePlan) -> AccessPolicy:
    operations = tuple(
        OperationAddress(instance.instance_id, operation.name)
        for instance in plan.instances
        for operation in instance.operations
    )
    permissions = tuple(
        Permission(rule.caller, OperationAddress(rule.target, name))
        for rule in plan.permissions
        for name in rule.operations
    )
    scheduled = {
        OperationAddress(node.target.component, node.target.operation) for node in plan.nodes
    }
    scheduled.add(OperationAddress(plan.controller.component, plan.controller.operation))
    return AccessPolicy(operations, permissions, tuple(sorted(scheduled)))
