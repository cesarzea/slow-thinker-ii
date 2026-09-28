"""Read the trusted bundled catalogue without accepting caller-supplied paths."""

from pathlib import Path

from slow_thinker_ii.definitions import GraphSummary, PlannedNode

from ._models import GraphRecord, SequenceConfig

BUNDLED = (
    "single-agent.graph.json",
    "handoff.graph.json",
    "review-cycle.graph.json",
    "repeated-review.graph.json",
)


class BundledDefinitionStore:
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def summaries(self) -> tuple[GraphSummary, ...]:
        return tuple(self._read(name) for name in BUNDLED)

    def _read(self, name: str) -> GraphSummary:
        graph = GraphRecord.model_validate_json((self._directory / name).read_bytes())
        steps = SequenceConfig.model_validate(
            graph.components[graph.controller.component].config
        ).steps
        if len(steps) != len(set(steps)) or set(steps) != set(graph.nodes):
            raise ValueError("Sequence steps must identify every planned node exactly once")
        nodes = tuple(PlannedNode(step, graph.nodes[step].component) for step in steps)
        return GraphSummary(graph.graph_id, graph.revision, nodes)

    def definition(self, graph_id: str, revision: str) -> str:
        matches: list[str] = []
        for name in BUNDLED:
            text = (self._directory / name).read_text()
            record = GraphRecord.model_validate_json(text)
            if (record.graph_id, record.revision) == (graph_id, revision):
                matches.append(text)
        if len(matches) != 1:
            raise ValueError("An exact bundled graph revision is required")
        return matches[0]
