"""Compact views of validation results for assertions."""

from slow_thinker_ii.catalog import ComponentDeclaration
from slow_thinker_ii.contracts import JsonObject
from slow_thinker_ii.graphs import Diagnostic, validate_document

from .contract_fixtures import step_one_catalog

type Found = tuple[str, str, str, str | None]  # code, path, message, node id


def validate(document: JsonObject, *extra: ComponentDeclaration) -> tuple[Diagnostic, ...]:
    return validate_document(document, step_one_catalog(*extra))


def found(document: JsonObject, *extra: ComponentDeclaration) -> list[Found]:
    return [
        (item.code, item.path, item.message, item.node_id) for item in validate(document, *extra)
    ]


def found_with(document: JsonObject, code: str, *extra: ComponentDeclaration) -> list[Found]:
    return [item for item in found(document, *extra) if item[0] == code]


def messages(
    document: JsonObject, code: str, *extra: ComponentDeclaration
) -> list[tuple[str, str]]:
    return [(path, message) for _, path, message, _ in found_with(document, code, *extra)]
