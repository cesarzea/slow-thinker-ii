"""Immutable configuration boundary for a packaged deterministic selector."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RedirectorConfig:
    outputs: tuple[str, ...]
    selector: str
    input_schema_json: str
