"""Small real installed components provide configurable contracts for graph admission tests."""

from pathlib import Path

from slow_thinker_ii.adapters.catalog import InstalledGraphCompiler, TypeInstallation
from slow_thinker_ii.adapters.installations import ComponentRegistration
from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from .installations import new_catalog
from .sequence_plans import EXAMPLES, SCHEMAS
from .wheels import lockfile, wheel

SOURCE = """from types import SimpleNamespace
class Component:
    @staticmethod
    def describe(config):
        if "steps" in config:
            return (SimpleNamespace(name="next", input_schema={"type":"object"},
                output_schema={"type":"object"}),)
        if "provider_profile" in config or "model_alias" in config:
            return (SimpleNamespace(name="complete", input_schema={"type":"object"},
                output_schema={"type":"object"}),)
        return (SimpleNamespace(name="generate", input_schema=config["input_schema"],
            output_schema={"type":"object"}),)
"""


def types(directory: Path) -> tuple[TypeInstallation, ...]:
    catalog = new_catalog(directory)
    artifact = wheel(directory, "graph-description", "1.0", SOURCE)
    lock = lockfile(directory, (artifact,))
    records: list[TypeInstallation] = []
    for filename in ("sequence", "llm-call", "model"):
        descriptor = (EXAMPLES / f"{filename}.component.json").read_text()
        manifest = json_object(decode_json(descriptor))
        registration = ComponentRegistration(
            type_id=str(manifest["type_id"]),
            type_version=str(manifest["type_version"]),
            distribution="graph-description",
            version="1.0",
            entry_point="graph_description:Component",
        )
        resolution = catalog.prepare(lock, directory, registration)
        records.append(TypeInstallation(resolution.identity, encode_json(manifest)))
    return tuple(records)


def compiler(directory: Path, selected: tuple[TypeInstallation, ...]) -> InstalledGraphCompiler:
    return InstalledGraphCompiler(new_catalog(directory), SCHEMAS, selected)
