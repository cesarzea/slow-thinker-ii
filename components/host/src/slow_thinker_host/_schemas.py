"""Validate self-contained schemas offline; patterns follow ECMA-262 like the platform."""

import importlib
import re
from collections.abc import Callable, Iterable, Iterator
from typing import cast

from jsonschema import Draft202012Validator
from jsonschema.exceptions import SchemaError, ValidationError
from jsonschema.protocols import Validator
from referencing import Registry
from referencing.exceptions import Unresolvable

from ._json import JsonObject, JsonValue
from ._patterns import python_pattern

type Keyword = Callable[[Validator, object, object, object], Iterator[ValidationError]]
type Extend = Callable[[type[Validator], dict[str, Keyword]], type[Validator]]
type BestMatch = Callable[[Iterable[ValidationError]], ValidationError | None]


def _references(value: JsonValue) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key in ("$ref", "$dynamicRef") and (
                not isinstance(item, str) or not item.startswith("#")
            ):
                raise ValueError("Only local schema references are supported")
            _references(item)
    elif isinstance(value, list):
        for item in value:
            _references(item)


def check_schema(schema: JsonObject) -> None:
    """Accept a draft 2020-12 schema whose references are all local."""
    _references(schema)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        raise ValueError(f"Invalid JSON Schema: {error.message}") from error


def validate_value(value: JsonValue, schema: JsonObject) -> None:
    """Raise ValueError naming the JSON Pointer and reason of the most relevant violation."""
    validator = _ecma_draft_2020_12()(schema, registry=Registry())
    # `best_match` has no return annotation; it is cast once to its documented signature.
    best_match = cast(BestMatch, importlib.import_module("jsonschema.exceptions").best_match)
    try:
        error = best_match(validator.iter_errors(value))
    except Unresolvable as unresolved:
        raise ValueError(f"Unresolvable schema reference: {unresolved}") from unresolved
    if error is not None:
        pointer = "".join(
            "/" + str(part).replace("~", "~0").replace("/", "~1") for part in error.absolute_path
        )
        raise ValueError(f"{pointer}: {error.message}" if pointer else error.message)


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
