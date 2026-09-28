"""UI-independent identities and the initial finite-sequence projection."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlannedNode:
    node_id: str
    component_id: str


@dataclass(frozen=True)
class GraphSummary:
    graph_id: str
    revision: str
    nodes: tuple[PlannedNode, ...]

    @property
    def participant_count(self) -> int:
        return len({node.component_id for node in self.nodes})
