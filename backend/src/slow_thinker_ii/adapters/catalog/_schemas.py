"""Resolve contract URNs only through the local schema catalogue; never fetch remote schemas."""

from pathlib import Path

from jsonschema import Draft202012Validator, validate
from referencing import Registry, Resource

from slow_thinker_ii.contracts import JsonValue, decode_json, json_object


class ContractSchemas:
    def __init__(self, directory: Path) -> None:
        registry = Registry[JsonValue]()
        for path in sorted(directory.glob("*.schema.json")):
            schema = json_object(decode_json(path.read_text()))
            Draft202012Validator.check_schema(schema)
            identity = schema.get("$id")
            if not isinstance(identity, str):
                raise ValueError("A contract schema must declare its identity")
            resource: Resource[JsonValue] = Resource.from_contents(schema)
            registry = registry.with_resource(identity, resource)
        self._registry = registry
        self._graph = json_object(decode_json((directory / "graph.schema.json").read_text()))

    def graph(self, value: JsonValue) -> None:
        validate(value, self._graph, cls=Draft202012Validator, registry=self._registry)

    def validate(self, value: JsonValue, schema_json: str) -> None:
        schema = json_object(decode_json(schema_json))
        Draft202012Validator.check_schema(schema)
        validate(value, schema, cls=Draft202012Validator, registry=self._registry)
