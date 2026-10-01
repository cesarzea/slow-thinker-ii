"""Immutable contract for a mediated worker and redirector composition."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RoutedCallConfig:
    input_schema_json: str
    worker_operation: str
    worker_output_schema_json: str
    router_input_pointer: str
    outputs: tuple[str, ...]
