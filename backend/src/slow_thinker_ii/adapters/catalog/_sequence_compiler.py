"""Compile the explicitly selected finite-sequence profile from canonical JSON contracts."""

from pathlib import Path

from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import (
    OperationTarget,
    PlanNode,
    PlanPermission,
    ResolvedInstance,
    SequencePlan,
)

from ._models import GraphRecord, SequenceConfig
from ._schemas import ContractSchemas
from ._sequence_nodes import compile_nodes
from ._sequence_references import operation, resolved_instances, resources


class SequenceCompiler:
    def __init__(self, schema_directory: Path) -> None:
        self._schemas = ContractSchemas(schema_directory)

    def compile(
        self, graph_json: str, input_json: str, instances: tuple[ResolvedInstance, ...]
    ) -> SequencePlan:
        value, run_input = (
            json_object(decode_json(graph_json)),
            json_object(decode_json(input_json)),
        )
        self._schemas.graph(value)
        graph = GraphRecord.model_validate(value)
        resolved = resolved_instances(graph, instances, self._schemas)
        controller = graph.controller
        operation(resolved, controller.component, controller.operation)
        if "control" not in resolved[controller.component].roles:
            raise ValueError("The selected controller must have the control role")
        config = SequenceConfig.model_validate(graph.components[controller.component].config)
        resources(graph, resolved)
        nodes = compile_nodes(graph, tuple(config.steps), run_input, resolved, self._schemas)
        return build_plan(graph, encode_json(value), encode_json(run_input), instances, nodes)


def build_plan(
    graph: GraphRecord,
    graph_json: str,
    input_json: str,
    instances: tuple[ResolvedInstance, ...],
    nodes: tuple[PlanNode, ...],
) -> SequencePlan:
    rules = tuple(
        PlanPermission(rule.caller, rule.target, tuple(rule.operations))
        for rule in graph.permissions
    )
    return SequencePlan(
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
    )
