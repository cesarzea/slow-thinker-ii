"""Resolve static inputs now and retain only backward node references for runtime binding."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json
from slow_thinker_ii.definitions import (
    OperationTarget,
    OutputArgument,
    PlanNode,
    ResolvedInstance,
    StaticArgument,
    node_arguments,
    pointer_tokens,
    read_pointer,
)

from ._models import BindingRecord, GraphRecord
from ._schemas import ContractSchemas
from ._sequence_references import operation


def compile_nodes(
    graph: GraphRecord,
    steps: tuple[str, ...],
    run_input: JsonObject,
    instances: Mapping[str, ResolvedInstance],
    schemas: ContractSchemas,
) -> tuple[PlanNode, ...]:
    if not steps or len(set(steps)) != len(steps) or set(steps) != set(graph.nodes):
        raise ValueError("The finite sequence must include every node exactly once")
    earlier: set[str] = set()
    result: list[PlanNode] = []
    for identity in steps:
        node = graph.nodes[identity]
        contract = operation(instances, node.component, node.operation)
        bindings = tuple(
            binding(name, value, run_input, earlier) for name, value in node.inputs.items()
        )
        planned = PlanNode(identity, OperationTarget(node.component, node.operation), bindings)
        if all(isinstance(item, StaticArgument) for item in bindings):
            from_arguments = node_arguments(planned, {})
            schemas.validate(decode_json(from_arguments), contract.input_schema_json)
        earlier.add(identity)
        result.append(planned)
    return tuple(result)


def binding(
    name: str, value: BindingRecord, run_input: JsonObject, earlier: set[str]
) -> StaticArgument | OutputArgument:
    if value.source == "literal":
        return StaticArgument(name, encode_json(value.value))
    pointer_tokens(value.pointer)
    if value.source == "run_input":
        return StaticArgument(name, encode_json(read_pointer(run_input, value.pointer)))
    if value.node is None or value.node not in earlier:
        raise ValueError("Node outputs must reference an earlier node in this sequence")
    return OutputArgument(name, value.node, value.pointer)
