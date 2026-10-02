"""Validate static arguments while deferring unavailable runtime binding values."""

import re
from typing import cast

from referencing import Registry

from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json, json_object

from .._models import BindingRecord
from ._diagnostics import pointer, require
from ._schemas import LocalSchemas, resource


def literals(
    bindings: dict[str, BindingRecord],
    schema: JsonObject,
    schemas: LocalSchemas,
    parts: tuple[str, ...],
) -> None:
    values: JsonObject = {
        name: value.value for name, value in bindings.items() if value.source == "literal"
    }
    if len(values) == len(bindings):
        schemas.validate(values, schema, parts)
        return
    for declared, owner in object_contracts(schema, schemas.registry(schema), schema):
        require(
            declared is not False, pointer(parts), "Input bindings cannot satisfy a false schema."
        )
        if isinstance(declared, dict):
            validate_arguments(bindings, declared, owner, schemas, parts)


def validate_arguments(
    bindings: dict[str, BindingRecord],
    declared: JsonObject,
    owner: JsonObject,
    schemas: LocalSchemas,
    parts: tuple[str, ...],
) -> None:
    names(bindings, declared, pointer(parts))
    for name, binding in bindings.items():
        for child in argument_schemas(name, declared):
            if binding.source != "literal":
                possible(child, owner, schemas, (*parts, name))
                continue
            validator = schemas.schema(owner, pointer(parts))
            for error in validator.descend(binding.value, child):
                require(
                    False,
                    pointer((*parts, name, *error.path)),
                    "Literal does not match its declared input schema.",
                )


def possible(
    schema: bool | JsonObject, owner: JsonObject, schemas: LocalSchemas, parts: tuple[str, ...]
) -> None:
    for declared, _ in object_contracts(schema, schemas.registry(owner), owner):
        require(
            declared is not False, pointer(parts), "Input binding cannot satisfy a false schema."
        )


def object_contracts(
    schema: bool | JsonObject, registry: Registry[JsonValue], owner: JsonObject
) -> list[tuple[bool | JsonObject, JsonObject]]:
    result: list[tuple[bool | JsonObject, JsonObject]] = []
    seen: set[str] = set()
    resolver = registry.resolver(str(owner.get("$id", ""))).in_subresource(resource(schema))
    pending = [(schema, owner, resolver)]
    while pending:
        current, owner, resolver = pending.pop()
        encoded = encode_json(current)
        if encoded in seen:
            continue
        seen.add(encoded)
        result.append((current, owner))
        if isinstance(current, bool):
            continue
        reference = current.get("$ref")
        if isinstance(reference, str):
            resolved = resolver.lookup(reference)
            target = cast(bool | JsonObject, resolved.contents)
            next_owner = owner if reference.startswith("#") or isinstance(target, bool) else target
            pending.append((target, next_owner, resolved.resolver))
        pending.extend(
            (child, owner, resolver.in_subresource(resource(child)))
            for child in intersections(current)
        )
    return result


def intersections(schema: JsonObject) -> list[bool | JsonObject]:
    children = schema.get("allOf", [])
    if not isinstance(children, list):
        return []
    return [child for child in children if isinstance(child, (bool, dict))]


def names(bindings: dict[str, BindingRecord], schema: JsonObject, path: str) -> None:
    required = schema.get("required", [])
    if isinstance(required, list):
        require(
            set(str(name) for name in required) <= set(bindings),
            path,
            "A required input binding is missing.",
        )
    if schema.get("additionalProperties") is False:
        require(
            all(argument_schemas(name, schema) for name in bindings),
            path,
            "Input binding name is not declared by the operation.",
        )


def argument_schemas(name: str, schema: JsonObject) -> list[bool | JsonObject]:
    properties = json_object(schema.get("properties", {}))
    patterns = json_object(schema.get("patternProperties", {}))
    matches = [value for pattern, value in patterns.items() if re.search(pattern, name)]
    if name in properties:
        matches.append(properties[name])
    if not matches and schema.get("additionalProperties") is not False:
        matches.append(schema.get("additionalProperties", {}))
    return [value for value in matches if isinstance(value, (bool, dict))]
