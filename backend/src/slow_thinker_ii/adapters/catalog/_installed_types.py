"""Validate trusted type descriptors and preserve explicit resource-operation requirements."""

from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    OperationContract,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_ii.definitions import ResolvedInstance, ResourceRequirement

from ._installed_records import TypeInstallation
from ._schemas import ContractSchemas


def strings(value: JsonValue) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise ValueError("Expected nonempty string identities")
    return tuple(str(item) for item in value)


def installed_types(
    values: tuple[TypeInstallation, ...], schemas: ContractSchemas, component_schema_json: str
) -> dict[tuple[str, str], TypeInstallation]:
    result: dict[tuple[str, str], TypeInstallation] = {}
    for item in values:
        manifest = json_object(decode_json(item.descriptor_json))
        schemas.validate(manifest, component_schema_json)
        key = str(manifest["type_id"]), str(manifest["type_version"])
        if key in result:
            raise ValueError("Select exactly one installation for each component type and version")
        result[key] = TypeInstallation(item.resolution_id, encode_json(manifest))
    return result


def resources(manifest: JsonObject) -> tuple[ResourceRequirement, ...]:
    values: list[ResourceRequirement] = []
    for name, item in json_object(manifest["resource_slots"]).items():
        record = json_object(item)
        required = record["required"]
        assert isinstance(required, bool)
        values.append(
            ResourceRequirement(
                name, str(record["role"]), required, strings(record.get("operations", []))
            )
        )
    return tuple(values)


def resolved_instance(
    identity: str, manifest: JsonObject, operations: tuple[OperationContract, ...]
) -> ResolvedInstance:
    declared = json_object(manifest["operations"])
    if set(declared) != {item.name for item in operations}:
        raise ValueError("Installed operation names differ from the type descriptor")
    if any(json_object(value)["mcp_tool"] != name for name, value in declared.items()):
        raise ValueError("The initial operation names must equal their MCP tool names")
    return ResolvedInstance(
        identity,
        str(manifest["type_id"]),
        str(manifest["type_version"]),
        encode_json(manifest["config_schema"]),
        strings(manifest["roles"]),
        operations,
        resources(manifest),
    )
