"""Finite ordering without retained workflow state or hidden scheduling logic."""

from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class Decision:
    action: Literal["schedule", "complete"]
    nodes: tuple[str, ...]


class Sequence:
    def __init__(self, steps: tuple[str, ...]) -> None:
        if not steps or any(not step for step in steps) or len(set(steps)) != len(steps):
            raise ValueError("Sequence steps must be nonempty and unique")
        self._steps = steps

    def next(self, completed_nodes: tuple[str, ...]) -> Decision:
        if completed_nodes != self._steps[: len(completed_nodes)]:
            raise ValueError("Completed activations must be an exact prefix of the sequence")
        index = len(completed_nodes)
        if index == len(self._steps):
            return Decision("complete", ())
        return Decision("schedule", (self._steps[index],))
