"""Independent installed descriptions let public compilation verify composition compatibility."""

from dataclasses import dataclass
from pathlib import Path

from slow_thinker_ii.adapters.catalog import InstalledGraphCompiler, TypeInstallation
from slow_thinker_ii.adapters.installations import ComponentRegistration
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object
from slow_thinker_ii.definitions import read_pointer

from .installations import new_catalog
from .sequence_plans import EXAMPLES, MANIFESTS, SCHEMAS, graph_value, resolved
from .wheels import lockfile, wheel

SOURCE = """from types import SimpleNamespace
class Component:
    @staticmethod
    def describe(config):
        return (SimpleNamespace(name=config['name'], input_schema=config['incoming'],
            output_schema=config['outgoing']),)
"""


@dataclass(frozen=True)
class CompositionInstallation:
    directory: Path
    selected: tuple[TypeInstallation, ...]

    def compiler(self) -> InstalledGraphCompiler:
        return InstalledGraphCompiler(new_catalog(self.directory), SCHEMAS, self.selected)


def prepare_composition(directory: Path) -> CompositionInstallation:
    catalog = new_catalog(directory)
    artifact = wheel(directory, "composition-description", "1.0", SOURCE)
    lock = lockfile(directory, (artifact,))
    selected: list[TypeInstallation] = []
    for type_id, filename in MANIFESTS.items():
        manifest = json_object(decode_json((EXAMPLES / filename).read_text()))
        if type_id == "routed-call":
            manifest["config_schema"] = {"type": "object"}
            manifest["resource_slots"] = {
                "worker": {"role": "agent", "required": False},
                "router": {"role": "resource", "required": False},
            }
        registration = ComponentRegistration(
            type_id=type_id,
            type_version=str(manifest["type_version"]),
            distribution="composition-description",
            version="1.0",
            entry_point="composition_description:Component",
        )
        record = catalog.prepare(lock, directory, registration)
        selected.append(TypeInstallation(record.identity, encode_json(manifest)))
    return CompositionInstallation(directory, tuple(selected))


def effective_descriptions() -> dict[str, str]:
    graph = graph_value("bounded-review")
    result: dict[str, str] = {}
    for instance in resolved(graph):
        operation = instance.operations[0]
        outgoing: JsonValue = decode_json(operation.output_schema_json)
        if instance.instance_id == "review-worker":
            outgoing = read_pointer(graph, "/components/reviewer/config/worker_output_schema")
        elif instance.instance_id == "review-router":
            outgoing = {"type": "object", "properties": {"port": {"enum": ["accept", "revise"]}}}
        result[instance.instance_id] = encode_json(
            {
                "name": operation.name,
                "incoming": decode_json(operation.input_schema_json),
                "outgoing": outgoing,
            }
        )
    return result


def change_object(graph: JsonObject, pointer: str) -> JsonObject:
    value = read_pointer(graph, pointer)
    assert isinstance(value, dict)
    return value
