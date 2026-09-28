"""Frozen sequence data uses JSON strings so caller mutation cannot alter admitted inputs."""

from dataclasses import dataclass

from slow_thinker_ii.contracts import OperationContract


@dataclass(frozen=True)
class OperationTarget:
    component: str
    operation: str


@dataclass(frozen=True)
class StaticArgument:
    name: str
    value_json: str


@dataclass(frozen=True)
class OutputArgument:
    name: str
    node: str
    pointer: str


@dataclass(frozen=True)
class PlanNode:
    node_id: str
    target: OperationTarget
    inputs: tuple[StaticArgument | OutputArgument, ...]


@dataclass(frozen=True)
class ResourceRequirement:
    slot: str
    role: str
    required: bool
    operations: tuple[str, ...] = ()


@dataclass(frozen=True)
class ResolvedInstance:
    instance_id: str
    type_id: str
    type_version: str
    config_schema_json: str
    roles: tuple[str, ...]
    operations: tuple[OperationContract, ...]
    resources: tuple[ResourceRequirement, ...]


@dataclass(frozen=True)
class PlanPermission:
    caller: str
    target: str
    operations: tuple[str, ...]


@dataclass(frozen=True)
class SequencePlan:
    graph_id: str
    revision: str
    controller: OperationTarget
    nodes: tuple[PlanNode, ...]
    instances: tuple[ResolvedInstance, ...]
    permissions: tuple[PlanPermission, ...]
    graph_json: str
    input_json: str
    limits_profile: str
    parent_json: str | None
