"""Resolve the documented example contracts without pretending they are installed packages."""

from pathlib import Path

from pydantic import TypeAdapter
from slow_thinker_ii.adapters.catalog import SequenceCompiler
from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    OperationContract,
    decode_json,
    encode_json,
    json_object,
)
from slow_thinker_ii.definitions import ResolvedInstance, ResourceRequirement, SequencePlan

from .resource_contracts import resource_descriptor_path, resource_operation

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "docs/contracts/examples"
SCHEMAS = ROOT / "docs/contracts/schemas"
STRINGS = TypeAdapter(tuple[str, ...])
MANIFESTS = {
    "llm-call": "llm-call.component.json",
    "routed-call": "routed-call.component.json",
    "redirector": "redirector.component.json",
    "bounded-flow": "bounded-flow.component.json",
    "example.model-resource": "model.component.json",
    "example.sequence": "sequence.component.json",
}


def graph_value(name: str) -> JsonObject:
    return json_object(decode_json((EXAMPLES / f"{name}.graph.json").read_text()))


def resolved(graph: JsonObject) -> tuple[ResolvedInstance, ...]:
    values = json_object(graph["components"])
    return tuple(
        resolve_instance(identity, json_object(value)) for identity, value in values.items()
    )


def resolve_instance(identity: str, spec: JsonObject) -> ResolvedInstance:
    type_id, version = str(spec["type_id"]), str(spec["type_version"])
    manifest = json_object(decode_json(manifest_path(type_id).read_text()))
    requirements = tuple(
        resource(name, json_object(value))
        for name, value in json_object(manifest["resource_slots"]).items()
    )
    return ResolvedInstance(
        identity,
        type_id,
        version,
        encode_json(manifest["config_schema"]),
        STRINGS.validate_python(manifest["roles"]),
        instance_operations(spec, manifest),
        requirements,
    )


def instance_operations(spec: JsonObject, manifest: JsonObject) -> tuple[OperationContract, ...]:
    type_id = str(spec["type_id"])
    operations: list[OperationContract] = []
    for name, value in json_object(manifest["operations"]).items():
        contract = json_object(value)
        input_schema = contract["input_schema"]
        if type_id == "llm-call" and name == "generate":
            input_schema = json_object(spec["config"])["input_schema"]
        input_schema, output_schema = resource_operation(
            type_id,
            name,
            json_object(spec["config"]),
            json_object(input_schema),
            json_object(contract["output_schema"]),
        )
        operations.append(
            OperationContract(name, encode_json(input_schema), encode_json(output_schema))
        )
    return tuple(operations)


def manifest_path(type_id: str) -> Path:
    return (
        EXAMPLES / MANIFESTS[type_id] if type_id in MANIFESTS else resource_descriptor_path(type_id)
    )


def resource(name: str, value: JsonObject) -> ResourceRequirement:
    required: JsonValue = value["required"]
    assert isinstance(required, bool)
    return ResourceRequirement(
        name, str(value["role"]), required, STRINGS.validate_python(value.get("operations", []))
    )


def plan(name: str) -> SequencePlan:
    graph = graph_value(name)
    return SequenceCompiler(SCHEMAS).compile(
        encode_json(graph), '{"problem":"Design a workshop"}', resolved(graph)
    )
