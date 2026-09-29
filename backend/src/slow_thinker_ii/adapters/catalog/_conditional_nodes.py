"""Compile explicit conditional arguments, selectors and declared output routes."""

from collections.abc import Mapping

from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json
from slow_thinker_ii.definitions import (
    ConditionalNode,
    LatestOutput,
    OperationTarget,
    OutputSelector,
    ResolvedInstance,
    StaticArgument,
    conditional_arguments,
    pointer_tokens,
    read_pointer,
)

from ._models import BindingRecord, ConditionalConfig, GraphRecord, NodeRecord
from ._schemas import ContractSchemas
from ._sequence_references import operation


def conditional_binding(
    name: str, value: BindingRecord, run_input: JsonObject
) -> StaticArgument | LatestOutput:
    if value.source == "literal":
        return StaticArgument(name, encode_json(value.value))
    pointer_tokens(value.pointer)
    if value.source == "run_input":
        return StaticArgument(name, encode_json(read_pointer(run_input, value.pointer)))
    if value.node is None or value.activation != "latest_completed":
        raise ValueError("Conditional output bindings require latest_completed activation")
    return LatestOutput(name, value.node, value.pointer, value.missing == "omit")


def selector(node: NodeRecord, ports: set[str]) -> OutputSelector:
    value = node.output
    if value is None or (value.constant is None) == (value.pointer is None):
        raise ValueError("Conditional nodes require exactly one output selector")
    if value.constant is not None and value.constant not in ports:
        raise ValueError("Constant selector must name a declared controller port")
    if value.pointer is not None:
        pointer_tokens(value.pointer)
    return OutputSelector(value.constant, value.pointer)


def conditional_nodes(
    graph: GraphRecord,
    config: ConditionalConfig,
    run_input: JsonObject,
    instances: Mapping[str, ResolvedInstance],
    schemas: ContractSchemas,
) -> tuple[ConditionalNode, ...]:
    result: list[ConditionalNode] = []
    for identity, node in graph.nodes.items():
        contract = operation(instances, node.component, node.operation)
        bindings = tuple(
            conditional_binding(name, value, run_input) for name, value in node.inputs.items()
        )
        if any(
            isinstance(item, LatestOutput) and item.node not in graph.nodes for item in bindings
        ):
            raise ValueError("Conditional bindings must reference declared nodes")
        planned = ConditionalNode(
            identity,
            OperationTarget(node.component, node.operation),
            bindings,
            selector(node, set(config.routes[identity])),
            tuple(config.routes[identity].items()),
        )
        validate_static(planned, contract.input_schema_json, schemas)
        result.append(planned)
    return tuple(result)


def validate_static(node: ConditionalNode, schema: str, schemas: ContractSchemas) -> None:
    if all(isinstance(item, StaticArgument) for item in node.inputs):
        schemas.validate(decode_json(conditional_arguments(node, ()).arguments_json), schema)
