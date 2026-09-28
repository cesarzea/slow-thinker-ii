"""Immutable operation contracts crossing application and transport boundaries."""

from dataclasses import dataclass


@dataclass(frozen=True)
class OperationContract:
    name: str
    input_schema_json: str
    output_schema_json: str


@dataclass(frozen=True)
class OperationResult:
    payload_json: str
    is_error: bool
