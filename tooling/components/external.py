"""Explicit registration, descriptor and independent source preparation boundaries."""

from dataclasses import dataclass
from pathlib import Path

from jsonschema import Draft202012Validator, validate
from slow_thinker_ii.adapters.catalog import validate_component_descriptor
from slow_thinker_ii.adapters.installations import ComponentRegistration, ImplementationBase
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object

from tooling.components.project import closure, project
from tooling.components.targets import PreparationTarget


@dataclass(frozen=True)
class ExternalTarget:
    recipe: PreparationTarget
    descriptor_name: str
    descriptor_json: str
    registration_json: str


def document(path: Path, schema: Path) -> JsonObject:
    value = json_object(decode_json(path.read_text(encoding="utf-8")))
    contract = json_object(decode_json(schema.read_text(encoding="utf-8")))
    validate(value, contract, cls=Draft202012Validator)
    return value


def registration(record: JsonObject) -> ComponentRegistration:
    distribution = json_object(record["distribution"])
    base = None
    if "base" in record:
        value = json_object(record["base"])
        base = ImplementationBase.model_validate(
            {
                "distribution": value["distribution"],
                "version": value["resolved_version"],
                "entry_point": value["entry_point"],
                "requirement": value["declared_requirement"],
            }
        )
    return ComponentRegistration.model_validate(
        {
            "type_id": record["type_id"],
            "type_version": record["type_version"],
            "distribution": distribution["name"],
            "version": distribution["version"],
            "entry_point": record["entry_point"],
            "base": base,
        }
    )


def external_target(
    root: Path,
    source: Path,
    registration_path: Path,
    descriptor_path: Path,
    dependencies: tuple[Path, ...] = (),
) -> ExternalTarget:
    schemas = root / "docs/contracts/schemas"
    record = document(registration_path, schemas / "python-registration.schema.json")
    descriptor = json_object(decode_json(descriptor_path.read_text(encoding="utf-8")))
    validate_component_descriptor(descriptor, schemas)
    registered = registration(record)
    if (descriptor["type_id"], descriptor["type_version"]) != (
        registered.type_id,
        registered.type_version,
    ):
        raise ValueError("External descriptor and registration identities disagree")
    primary = project(source)
    if (primary.name, primary.version) != (registered.distribution, registered.version):
        raise ValueError("External project and registration distributions disagree")
    descriptor_name = record["descriptor"]
    if not isinstance(descriptor_name, str) or descriptor_name != descriptor_path.name:
        raise ValueError("External registration must name the supplied descriptor")
    projects = closure(primary, dependencies)
    recipe = PreparationTarget(
        tuple(str(item.path) for item in projects),
        registered,
        tuple(item.requirement for item in projects[1:]),
    )
    return ExternalTarget(recipe, descriptor_name, encode_json(descriptor), encode_json(record))
