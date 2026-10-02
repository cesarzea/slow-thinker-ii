"""Check JSON schemas and resolve references exclusively through local resources."""

from collections.abc import Iterator
from pathlib import Path
from typing import Protocol, cast
from urllib.parse import urljoin

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from referencing import Registry, Resource
from referencing.exceptions import Unresolvable
from referencing.jsonschema import DRAFT202012, UnknownDialect

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

from ._diagnostics import pointer, reject


class SchemaValidator(Protocol):
    def iter_errors(self, instance: JsonValue) -> Iterator[ValidationError]: ...
    def descend(
        self, instance: JsonValue, schema: bool | JsonObject
    ) -> Iterator[ValidationError]: ...


class ValidatorFactory(Protocol):
    def __call__(self, schema: JsonObject, *, registry: Registry[JsonValue]) -> SchemaValidator: ...


class LocalSchemas:
    def __init__(self, directory: Path) -> None:
        self._schemas: dict[str, JsonObject] = {}
        registry = Registry[JsonValue]()
        for path in sorted(directory.glob("*.schema.json")):
            schema = json_object(decode_json(path.read_text(encoding="utf-8")))
            Draft202012Validator.check_schema(schema)
            identity = schema.get("$id")
            if not isinstance(identity, str) or identity in self._schemas:
                raise ValueError("Local schemas require unique identities")
            self._schemas[identity] = schema
            registry = registry.with_resource(identity, resource(schema))
        self._registry = registry.crawl()
        self.graph = json_object(decode_json((directory / "graph.schema.json").read_text()))
        self.component = json_object(decode_json((directory / "component.schema.json").read_text()))

    def schema(self, schema: JsonObject, path: str) -> SchemaValidator:
        try:
            Draft202012Validator.check_schema(schema)
            identity = str(schema.get("$id", ""))
            registry = self.registry(schema)
            check_references(resource(schema), registry, identity)
            # The external stubs use invariant schemas; the registry contains checked schemas only.
            return cast(ValidatorFactory, Draft202012Validator)(schema, registry=registry)
        except (ValueError, SchemaError, Unresolvable, UnknownDialect, RecursionError):
            reject(path, "Schema is invalid or references an unavailable local schema.")

    def document(self, identity: str) -> JsonObject:
        return json_object(self._schemas[identity])

    def registry(self, schema: JsonObject) -> Registry[JsonValue]:
        return self._registry.with_resource(str(schema.get("$id", "")), resource(schema)).crawl()

    def validate(self, value: JsonValue, schema: JsonObject, parts: tuple[str | int, ...]) -> None:
        validator = self.schema(schema, pointer(parts))
        issues: list[library.DefinitionIssue] = []
        for error in validator.iter_errors(value):
            issues.append(
                library.DefinitionIssue(
                    pointer((*parts, *error.absolute_path)),
                    "Value does not match its declared schema.",
                )
            )
            if len(issues) == 10:
                break
        if issues:
            raise library.DefinitionError("invalid_definition", tuple(issues))


def resource(schema: JsonValue) -> Resource[JsonValue]:
    return Resource.from_contents(schema, default_specification=DRAFT202012)


def schema_children(schema: JsonObject) -> Iterator[tuple[str, JsonObject]]:
    for name in ("input_schema", "worker_output_schema"):
        value = schema.get(name)
        if isinstance(value, dict):
            yield name, value
    output = schema.get("output")
    if isinstance(output, dict) and isinstance(output.get("schema"), dict):
        yield "output/schema", json_object(output["schema"])


def check_references(item: Resource[JsonValue], registry: Registry[JsonValue], base: str) -> None:
    resolver = registry.resolver(base)
    contents = item.contents
    if isinstance(contents, dict):
        for name in ("$ref", "$dynamicRef"):
            reference = contents.get(name)
            if isinstance(reference, str):
                resolver.lookup(reference)
    for child in item.subresources():
        identity = child.id()
        check_references(child, registry, base if identity is None else urljoin(base, identity))
