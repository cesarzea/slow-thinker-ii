"""Resolve exact local descriptors and declared per-instance operation schemas."""

from pathlib import Path

from slow_thinker_ii.contracts import (
    JsonObject,
    OperationContract,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_ii.definitions import ResolvedInstance

from .._installed_types import resolved_instance
from .._models import ComponentRecord, GraphRecord
from ._configuration import configured_policy, uses_llm_contract
from ._diagnostics import pointer, require
from ._schemas import LocalSchemas, schema_children
from ._specialized import llm_output, redirector_schemas, routed_schemas


def descriptors(
    directory: Path, schemas: LocalSchemas, extra: tuple[str, ...] = ()
) -> dict[tuple[str, str], JsonObject]:
    result: dict[tuple[str, str], JsonObject] = {}
    sources = (
        tuple(
            path.read_text(encoding="utf-8") for path in sorted(directory.glob("*.component.json"))
        )
        + extra
    )
    for source in sources:
        value = json_object(decode_json(source))
        schemas.validate(value, schemas.component, ())
        key = str(value["type_id"]), str(value["type_version"])
        if key in result and result[key] != value:
            raise ValueError("Local component descriptors require unique identities")
        result[key] = value
    return result


def instances(
    graph: GraphRecord, directory: Path, schemas: LocalSchemas, extra: tuple[str, ...] = ()
) -> dict[str, ResolvedInstance]:
    registered = descriptors(directory, schemas, extra)
    result: dict[str, ResolvedInstance] = {}
    for identity, component in graph.components.items():
        parts = ("components", identity)
        key = component.type_id, component.type_version
        require(
            key in registered, pointer(parts), "The exact component type version is not registered."
        )
        manifest = registered[key]
        schemas.validate(
            component.config, json_object(manifest["config_schema"]), (*parts, "config")
        )
        for name, schema in schema_children(component.config):
            schemas.schema(schema, pointer((*parts, "config", *name.split("/"))))
        configured_policy(identity, component, manifest)
        result[identity] = resolved_instance(
            identity, manifest, operations(component, manifest, schemas)
        )
    return result


def operations(
    component: ComponentRecord, manifest: JsonObject, schemas: LocalSchemas
) -> tuple[OperationContract, ...]:
    values: list[OperationContract] = []
    for name, value in json_object(manifest["operations"]).items():
        record = json_object(value)
        input_schema, output_schema = specialize(component, manifest, name, record, schemas)
        schemas.schema(input_schema, "")
        schemas.schema(output_schema, "")
        values.append(
            OperationContract(name, encode_json(input_schema), encode_json(output_schema))
        )
    return tuple(values)


def specialize(
    component: ComponentRecord,
    manifest: JsonObject,
    name: str,
    record: JsonObject,
    schemas: LocalSchemas,
) -> tuple[JsonObject, JsonObject]:
    config, kind = component.config, component.type_id
    input_schema = json_object(record["input_schema"])
    output_schema = json_object(record["output_schema"])
    if uses_llm_contract(manifest["config_schema"]) and name == "generate":
        input_schema = json_object(config["input_schema"])
        output_schema = llm_output(config, schemas)
    if kind == "routed-call" and name == "invoke":
        input_schema, output_schema = routed_schemas(config)
    if kind == "contextual-call" and name == "invoke":
        input_schema = json_object(config["input_schema"])
        output_schema = json_object(config["worker_output_schema"])
    if kind == "redirector" and name == "route":
        input_schema, output_schema = redirector_schemas(config)
    return input_schema, output_schema
