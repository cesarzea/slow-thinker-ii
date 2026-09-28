"""Read a platform-written bootstrap record; it cannot select executable code."""

from dataclasses import dataclass, field
from pathlib import Path

from ._contracts import Operation
from ._json import JsonObject, decode_json, json_object


@dataclass(frozen=True)
class Bootstrap:
    config: JsonObject
    operations: tuple[Operation, ...]
    clients: JsonObject = field(default_factory=lambda: json_object({}))


def read_bootstrap(path: Path) -> Bootstrap:
    record = json_object(decode_json(path.read_text(encoding="utf-8")))
    if not {"config", "operations"} <= set(record) or set(record) - {
        "config",
        "operations",
        "clients",
    }:
        raise ValueError("Unsupported bootstrap fields")
    operations = record["operations"]
    if not isinstance(operations, list):
        raise ValueError("Bootstrap operations must be an array")
    return Bootstrap(
        json_object(record["config"]),
        tuple(_operation(item) for item in operations),
        json_object(record.get("clients", {})),
    )


def _operation(value: object) -> Operation:
    record = json_object(value)
    if set(record) != {"name", "input_schema", "output_schema"}:
        raise ValueError("Unsupported operation fields")
    name = record["name"]
    if not isinstance(name, str) or not name:
        raise ValueError("Invalid operation name")
    return Operation(
        name, json_object(record["input_schema"]), json_object(record["output_schema"])
    )
