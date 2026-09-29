"""Immutable topology, history and decision contracts for bounded control flow."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class FlowRoute:
    node: str
    port: str
    target: str | None


@dataclass(frozen=True)
class BoundedFlowConfig:
    entry: str
    routes: tuple[FlowRoute, ...]
    max_activations: int


@dataclass(frozen=True)
class CompletedStep:
    node: str
    port: str


@dataclass(frozen=True)
class FlowDecision:
    action: Literal["activate", "complete", "exhausted"]
    node: str | None = None
    reason: str | None = None
