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
from ._configuration import configured_policy
from ._diagnostics import pointer, require
from ._schemas import LocalSchemas, schema_children


def descriptors(directory: Path, schemas: LocalSchemas) -> dict[tuple[str, str], JsonObject]:
    result: dict[tuple[str, str], JsonObject] = {}
    for path in sorted(directory.glob("*.component.json")):
        value = json_object(decode_json(path.read_text(encoding="utf-8")))
        schemas.validate(value, schemas.component, ())
        key = str(value["type_id"]), str(value["type_version"])
        if key in result:
            raise ValueError("Local component descriptors require unique identities")
        result[key] = value
    return result


def instances(
    graph: GraphRecord, directory: Path, schemas: LocalSchemas
) -> dict[str, ResolvedInstance]:
    registered = descriptors(directory, schemas)
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
        input_schema, output_schema = specialize(component, name, record, schemas)
        schemas.schema(input_schema, "")
        schemas.schema(output_schema, "")
        values.append(
            OperationContract(name, encode_json(input_schema), encode_json(output_schema))
        )
    return tuple(values)


def specialize(
    component: ComponentRecord, name: str, record: JsonObject, schemas: LocalSchemas
) -> tuple[JsonObject, JsonObject]:
    config, kind = component.config, component.type_id
    input_schema = json_object(record["input_schema"])
    output_schema = json_object(record["output_schema"])
    if kind in {"llm-call", "example.grounded-review"} and name == "generate":
        input_schema = json_object(config["input_schema"])
        output_schema = llm_output(config, schemas)
    if kind == "routed-call" and name == "invoke":
        input_schema, output_schema = routed_schemas(config)
    if kind == "redirector" and name == "route":
        input_schema, output_schema = redirector_schemas(config)
    return input_schema, output_schema


def routed_schemas(config: JsonObject) -> tuple[JsonObject, JsonObject]:
    worker_schema = json_object(config["worker_output_schema"])
    worker_schema.setdefault("$id", "urn:slow-thinker-ii:routed-worker-output")
    output = object_schema(
        {
            "status": {"const": "succeeded"},
            "port": {"enum": config["outputs"]},
            "value": worker_schema,
        }
    )
    return json_object(config["input_schema"]), output


def redirector_schemas(config: JsonObject) -> tuple[JsonObject, JsonObject]:
    value_schema = json_object(config["input_schema"])
    value_schema.setdefault("$id", "urn:slow-thinker-ii:redirector-input")
    return object_schema({"value": value_schema}), object_schema(
        {"port": {"enum": config["outputs"]}}
    )


def llm_output(config: JsonObject, schemas: LocalSchemas) -> JsonObject:
    output = json_object(config["output"])
    value: JsonObject = (
        {"type": "string"} if output["format"] == "text" else json_object(output["schema"])
    )
    value.setdefault("$id", "urn:slow-thinker-ii:llm-output")
    success = object_schema(
        {"status": {"const": "ok"}, "format": {"const": output["format"]}, "value": value}
    )
    branches = schemas.document("urn:slow-thinker-ii:contracts:llm-call-result:0.1-draft")["oneOf"]
    if not isinstance(branches, list):
        raise ValueError("Local result schema must declare envelope alternatives")
    return {"type": "object", "oneOf": [success, branches[-1]]}


def object_schema(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
