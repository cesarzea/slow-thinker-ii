"""Read the trusted bundled catalogue without accepting caller-supplied paths."""

from pathlib import Path

from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from slow_thinker_ii.definitions import GraphSummary, PlannedNode, graph_detail, graph_input_schema

from ._graph_validation import validate_graph_input
from ._models import GraphRecord, SequenceConfig
from ._schemas import ContractSchemas

BUNDLED = (
    "single-agent.graph.json",
    "handoff.graph.json",
    "review-cycle.graph.json",
    "repeated-review.graph.json",
    "bounded-review.graph.json",
)


class BundledDefinitionStore:
    def __init__(self, directory: Path) -> None:
        self._directory = directory

    def summaries(self) -> tuple[GraphSummary, ...]:
        return tuple(self._read(name) for name in BUNDLED)

    def _read(self, name: str) -> GraphSummary:
        graph = GraphRecord.model_validate_json((self._directory / name).read_bytes())
        steps = (
            list(graph.nodes)
            if graph.execution_profile == "bounded-conditional"
            else SequenceConfig.model_validate(
                graph.components[graph.controller.component].config
            ).steps
        )
        if len(steps) != len(set(steps)) or set(steps) != set(graph.nodes):
            raise ValueError("Sequence steps must identify every planned node exactly once")
        nodes = tuple(PlannedNode(step, graph.nodes[step].component) for step in steps)
        value = json_object(decode_json((self._directory / name).read_text()))
        return GraphSummary(
            graph.graph_id, graph.revision, nodes, encode_json(graph_input_schema(value))
        )

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

    def detail(self, graph_id: str, revision: str) -> str:
        definition = json_object(decode_json(self.definition(graph_id, revision)))
        schemas = ContractSchemas(self._directory.parent / "schemas")
        schemas.graph(definition)
        graph = GraphRecord.model_validate(definition)
        # Input validation occurs on admission; this checks containment independently.
        validate_graph_input(graph.model_copy(update={"input_schema": None}), {}, schemas)
        types: dict[tuple[str, str], tuple[str, ...]] = {}
        for path in self._directory.glob("*.component.json"):
            descriptor = json_object(decode_json(path.read_text()))
            roles = descriptor.get("roles", [])
            if not isinstance(roles, list) or any(not isinstance(role, str) for role in roles):
                raise ValueError("Component roles must be declared strings")
            types[(str(descriptor["type_id"]), str(descriptor["type_version"]))] = tuple(
                str(role) for role in roles
            )
        roles_by_id: dict[str, tuple[str, ...]] = {}
        for identity, value in json_object(definition["components"]).items():
            component = json_object(value)
            key = str(component["type_id"]), str(component["type_version"])
            if key not in types:
                raise ValueError("Graph detail requires the exact component descriptor")
            roles_by_id[identity] = types[key]
        return encode_json(graph_detail(definition, roles_by_id))
