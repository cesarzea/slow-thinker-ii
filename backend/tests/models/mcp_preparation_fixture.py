"""Describe-only resource installations and public launch-profile recording."""

from pathlib import Path

from slow_thinker_ii.adapters.catalog import TypeInstallation
from slow_thinker_ii.adapters.installations import ComponentRegistration
from slow_thinker_ii.adapters.preparation import HostAdapter, HostProfile, HostRequest
from slow_thinker_ii.adapters.resources import MemoryResourceAdapter
from slow_thinker_ii.contracts import JsonObject, decode_json, encode_json, json_object
from support.installations import new_catalog
from support.preparation import PreparationCase
from support.sequence_plans import ROOT
from support.wheels import lockfile, wheel

from .preparation_fixture import Definitions


class ProfileRecorder:
    def __init__(self, adapter: HostAdapter) -> None:
        self.adapter = adapter
        self.profiles: dict[str, HostProfile] = {}

    def configure(self, request: HostRequest) -> HostProfile:
        profile = self.adapter.configure(request)
        self.profiles[request.instance_id] = profile
        return profile


def resource_installations(directory: Path) -> tuple[TypeInstallation, ...]:
    catalog = new_catalog(directory)
    records: list[TypeInstallation] = []
    build = directory / "resource-descriptions"
    build.mkdir()
    for name in ("calculator", "key-value-memory"):
        descriptor = (ROOT / f"components/{name}/{name}.component.json").read_text()
        manifest = json_object(decode_json(descriptor))
        distribution = f"{name}-description"
        artifact = wheel(build, distribution, "1.0", description_source(manifest["operations"]))
        registration = ComponentRegistration(
            type_id=name,
            type_version="0.1.0",
            distribution=distribution,
            version="1.0",
            entry_point=f"{distribution.replace('-', '_')}:Component",
        )
        record = catalog.prepare(lockfile(build, (artifact,)), build, registration)
        records.append(TypeInstallation(record.identity, descriptor))
    return tuple(records)


def description_source(operations: object) -> str:
    return f"""import json
from types import SimpleNamespace
OPERATIONS = json.loads({encode_json(json_object(operations))!r})
class Component:
    @staticmethod
    def describe(config):
        del config
        return tuple(SimpleNamespace(name=name, input_schema=value['input_schema'],
            output_schema=value['output_schema']) for name, value in OPERATIONS.items())
"""


def add_resources(
    case: PreparationCase, definitions: Definitions, records: tuple[TypeInstallation, ...]
) -> None:
    installations = case.settings["installations"]
    assert isinstance(installations, list)
    for record in records:
        descriptor = json_object(decode_json(record.descriptor_json))
        installations.append(
            {
                "type_id": descriptor["type_id"],
                "type_version": descriptor["type_version"],
                "resolution_id": record.resolution_id,
                "host_adapter": "memory"
                if descriptor["type_id"] == "key-value-memory"
                else "plain",
            }
        )
    case.descriptors += tuple(record.descriptor_json for record in records)
    case.adapters["memory"] = MemoryResourceAdapter(case.directory / "state")
    case.update()
    source = json_object(decode_json(definitions.source))
    components = json_object(source["components"])
    components["calculator"] = resource("calculator", {})
    components["memory"] = resource("key-value-memory", {"namespace": "regression"})
    source["components"] = components
    definitions.source = encode_json(source)


def resource(identity: str, config: JsonObject) -> JsonObject:
    return {"type_id": identity, "type_version": "0.1.0", "config": config, "resources": {}}
