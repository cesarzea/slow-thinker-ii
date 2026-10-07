"""Typed JSON Schema checks; the only catalog module that uses jsonschema's untyped API."""

import importlib
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from typing import cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import ValidationError
from jsonschema.protocols import Validator
from referencing import Registry
from referencing.exceptions import Unresolvable

from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    format_pointer,
    json_object,
    json_value,
    value_at_pointer,
)

from ._patterns import python_pattern
from ._values import mapping, member

type Keyword = Callable[[Validator, object, object, object], Iterator[ValidationError]]
type Extend = Callable[[type[Validator], dict[str, Keyword]], type[Validator]]


@dataclass(frozen=True)
class Violation:
    location: tuple[str, ...]  # of the offending value inside the instance
    keyword: str  # the failing keyword; empty for a `false` schema
    value: JsonValue  # the keyword's value in the schema


def instance_problems(schema: JsonObject, instance: JsonValue) -> list[tuple[str, str]]:
    """(pointer, message) for each way `instance` violates `schema`, in pointer order."""
    errors = _validator(schema).iter_errors(instance)
    return sorted({(format_pointer(error.absolute_path), error.message) for error in errors})


def metaschema_problems(schema: JsonObject) -> list[tuple[str, str]]:
    """(pointer, message) for each way `schema` violates the draft 2020-12 metaschema."""
    errors = _schema_validator().iter_errors(schema)
    return sorted({(format_pointer(error.absolute_path), error.message) for error in errors})


def violations(schema: JsonObject, instance: JsonValue) -> list[Violation]:
    """Each violation located at the exact offending value, including missing members."""
    try:
        errors = list(_validator(schema).iter_errors(instance))
    except Unresolvable:
        return [Violation((), "$ref", None)]
    return [found for error in errors for found in _located(schema, instance, error)]


def _validator(schema: JsonObject) -> Validator:
    # An empty registry keeps validation offline: unknown references fail, nothing is fetched.
    return _ecma_draft_2020_12()(schema, registry=Registry())


def _schema_validator() -> Validator:
    empty: JsonObject = {}
    probe = _validator(empty)
    metaschema = json_object(cast(object, probe.META_SCHEMA))
    checker = probe.FORMAT_CHECKER
    return _ecma_draft_2020_12()(metaschema, registry=Registry(), format_checker=checker)


def _ecma_draft_2020_12() -> type[Validator]:
    """Draft 2020-12 whose `pattern` keyword follows ECMA-262 instead of Python's `re`."""
    # `extend` has no annotations; it is cast once to the only signature used here.
    extend = cast(Extend, importlib.import_module("jsonschema.validators").extend)
    empty: JsonObject = {}
    return extend(type(Draft202012Validator(empty)), {"pattern": _ecma_pattern})


def _ecma_pattern(
    _validator: Validator, pattern: object, instance: object, _schema: object
) -> Iterator[ValidationError]:
    if not isinstance(pattern, str) or not isinstance(instance, str):
        return
    if re.search(python_pattern(pattern), instance) is None:
        yield ValidationError(f"{instance!r} does not match {pattern!r}")


def _located(schema: JsonObject, instance: JsonValue, error: ValidationError) -> list[Violation]:
    location = _location(instance, error)
    keyword = error.validator if isinstance(error.validator, str) else ""
    value = json_value(cast(object, error.validator_value))
    present = mapping(value_at_pointer(instance, location))
    if keyword == "required":
        names = [name for name in _strings(value) if name not in present]
    elif keyword == "additionalProperties":
        names = _unexpected(present, json_value(cast(object, error.schema)))
    elif keyword == "":
        properties = value_at_pointer(schema, (str(token) for token in error.relative_schema_path))
        names = _forbidden(present, properties)
    else:
        names = []
    if not names:
        return [Violation(location, keyword, value)]
    return [Violation((*location, name), keyword, value) for name in names]


def _location(instance: JsonValue, error: ValidationError) -> tuple[str, ...]:
    """Where the offending value is; a name refused by `propertyNames` is its own member."""
    location = tuple(str(token) for token in error.absolute_path)
    name = cast(object, error.instance)
    target = mapping(value_at_pointer(instance, location))
    if isinstance(name, str) and name in target and "propertyNames" in error.relative_schema_path:
        return (*location, name)
    return location


def _strings(value: JsonValue) -> list[str]:
    return [item for item in value if isinstance(item, str)] if isinstance(value, list) else []


def _unexpected(present: JsonObject, schema: JsonValue) -> list[str]:
    """Members that the schema's `additionalProperties: false` rejects."""
    declared = mapping(member(schema, "properties"))
    patterns = list(mapping(member(schema, "patternProperties")))
    return [
        name
        for name in present
        if name not in declared and not any(re.search(pattern, name) for pattern in patterns)
    ]


def _forbidden(present: JsonObject, properties: JsonValue) -> list[str]:
    """Members whose property schema is `false`; jsonschema does not report their location."""
    declared = mapping(properties)
    return [name for name in present if declared.get(name) is False]
