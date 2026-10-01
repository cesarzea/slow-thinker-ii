"""Immutable conditional plans retain each successful activation and its source references."""

from dataclasses import dataclass

from ._plans import OperationTarget, PlanPermission, ResolvedInstance, StaticArgument


@dataclass(frozen=True)
class LatestOutput:
    name: str
    node: str
    pointer: str
    omit_missing: bool = False


@dataclass(frozen=True)
class OutputSelector:
    constant: str | None = None
    pointer: str | None = None


@dataclass(frozen=True)
class ConditionalNode:
    node_id: str
    target: OperationTarget
    inputs: tuple[StaticArgument | LatestOutput, ...]
    output: OutputSelector
    routes: tuple[tuple[str, str | None], ...]


@dataclass(frozen=True)
class ConditionalPlan:
    graph_id: str
    revision: str
    controller: OperationTarget
    nodes: tuple[ConditionalNode, ...]
    instances: tuple[ResolvedInstance, ...]
    permissions: tuple[PlanPermission, ...]
    graph_json: str
    input_json: str
    limits_profile: str
    parent_json: str | None
    entry: str
    max_activations: int
    result: LatestOutput


@dataclass(frozen=True)
class CompletedActivation:
    node: str
    activation_id: str
    payload_id: str
    output_json: str
    port: str


@dataclass(frozen=True)
class BoundArguments:
    arguments_json: str
    sources_json: str
