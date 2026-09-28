"""Typed JSON documents; canonical contract schemas remain the structural authority."""

from typing import Literal

from pydantic import BaseModel, Field

from slow_thinker_ii.contracts import JsonObject, JsonValue


class Record(BaseModel, extra="forbid", strict=True, frozen=True):
    """Keep document conversion strict before building immutable domain values."""


class BindingRecord(Record, frozen=True):
    source: Literal["literal", "run_input", "node_output"]
    value: JsonValue = None
    pointer: str = ""
    node: str | None = None


class NodeRecord(Record, frozen=True):
    component: str
    operation: str
    inputs: dict[str, BindingRecord]


class SequenceConfig(Record, frozen=True):
    steps: list[str]


class ComponentRecord(Record, frozen=True):
    type_id: str
    type_version: str
    config: JsonObject
    resources: dict[str, str]


class ControllerRecord(Record, frozen=True):
    component: str
    operation: str


class PermissionRecord(Record, frozen=True):
    caller: str
    target: str
    operations: list[str]


class GraphRecord(Record, frozen=True):
    schema_version: Literal["0.1-draft"]
    graph_id: str
    revision: str
    controller: ControllerRecord
    components: dict[str, ComponentRecord]
    nodes: dict[str, NodeRecord]
    permissions: list[PermissionRecord]
    limits_profile: str
    derived_from: JsonObject | None = None
    extensions: JsonObject = Field(default_factory=dict)
