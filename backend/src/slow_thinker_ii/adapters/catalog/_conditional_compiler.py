"""Compile bounded collaboration without weakening the finite Sequence profile."""

from pathlib import Path

from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import (
    ConditionalNode,
    ConditionalPlan,
    LatestOutput,
    OperationTarget,
    PlanPermission,
    ResolvedInstance,
)

from ._conditional_nodes import conditional_binding, conditional_nodes
from ._graph_validation import validate_graph_input
from ._models import ConditionalConfig, GraphRecord
from ._schemas import ContractSchemas
from ._sequence_references import operation, resolved_instances, resources


class ConditionalCompiler:
    def __init__(self, schema_directory: Path) -> None:
        self._schemas = ContractSchemas(schema_directory)

    def compile(
        self, graph_json: str, input_json: str, instances: tuple[ResolvedInstance, ...]
    ) -> ConditionalPlan:
        value, run_input = (
            json_object(decode_json(graph_json)),
            json_object(decode_json(input_json)),
        )
        self._schemas.graph(value)
        graph = GraphRecord.model_validate(value)
        if graph.execution_profile != "bounded-conditional":
            raise ValueError("Conditional compilation requires its declared profile")
        validate_graph_input(graph, run_input, self._schemas)
        resolved = resolved_instances(graph, instances, self._schemas)
        controller = graph.controller
        operation(resolved, controller.component, controller.operation)
        if "control" not in resolved[controller.component].roles:
            raise ValueError("Conditional controller requires the control role")
        config = ConditionalConfig.model_validate(graph.components[controller.component].config)
        validate_routes(graph, config)
        resources(graph, resolved)
        nodes = conditional_nodes(graph, config, run_input, resolved, self._schemas)
        return build_plan(
            graph, config, nodes, instances, encode_json(value), encode_json(run_input)
        )


def validate_routes(graph: GraphRecord, config: ConditionalConfig) -> None:
    if config.entry not in graph.nodes or set(config.routes) != set(graph.nodes):
        raise ValueError("Conditional routes must cover every declared node")
    for routes in config.routes.values():
        if not routes or any(not port for port in routes):
            raise ValueError("Declare nonempty output ports for each node")
        if any(target is not None and target not in graph.nodes for target in routes.values()):
            raise ValueError("Conditional destinations must be declared nodes or terminal")


def build_plan(
    graph: GraphRecord,
    config: ConditionalConfig,
    nodes: tuple[ConditionalNode, ...],
    instances: tuple[ResolvedInstance, ...],
    graph_json: str,
    input_json: str,
) -> ConditionalPlan:
    result = result_binding(graph)
    rules = tuple(
        PlanPermission(item.caller, item.target, tuple(item.operations))
        for item in graph.permissions
    )
    return ConditionalPlan(
        graph.graph_id,
        graph.revision,
        OperationTarget(graph.controller.component, graph.controller.operation),
        nodes,
        instances,
        rules,
        graph_json,
        input_json,
        graph.limits_profile,
        None if graph.derived_from is None else encode_json(graph.derived_from),
        config.entry,
        config.max_activations,
        result,
    )


def result_binding(graph: GraphRecord) -> LatestOutput:
    if graph.result is None:
        raise ValueError("Conditional graphs require an explicit final output binding")
    result = conditional_binding("result", graph.result, {})
    if (
        not isinstance(result, LatestOutput)
        or result.node not in graph.nodes
        or result.omit_missing
    ):
        raise ValueError("Final output must select a required completed node activation")
    return result
