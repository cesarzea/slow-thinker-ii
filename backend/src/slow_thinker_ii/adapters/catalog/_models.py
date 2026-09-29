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
    activation: Literal["latest_completed"] | None = None
    missing: Literal["omit"] | None = None


class OutputRecord(Record, frozen=True):
    constant: str | None = None
    pointer: str | None = None


class ConditionalConfig(Record, frozen=True):
    entry: str
    routes: dict[str, dict[str, str | None]]
    max_activations: int = Field(gt=0)


class NodeRecord(Record, frozen=True):
    component: str
    operation: str
    inputs: dict[str, BindingRecord]
    output: OutputRecord | None = None


class SequenceConfig(Record, frozen=True):
    steps: list[str]


class ComponentRecord(Record, frozen=True):
    type_id: str
    type_version: str
    config: JsonObject
    resources: dict[str, str]
    contained_by: str | None = None


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
    execution_profile: Literal["sequence", "bounded-conditional"] = "sequence"
    input_schema: JsonObject | None = None
    result: BindingRecord | None = None
    derived_from: JsonObject | None = None
    extensions: JsonObject = Field(default_factory=dict)
