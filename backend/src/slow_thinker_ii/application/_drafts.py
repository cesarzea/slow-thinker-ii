"""Draft documents of a working copy: what must hold before a change is stored."""

import json
import re
from collections.abc import Iterable

from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json, json_object, parse_pointer
from slow_thinker_ii.graphs import Diagnostic, GraphInvalid

MAX_DRAFT_BYTES = 1_048_576
_DRAFT_PATHS = frozenset({"", "/format", "/id", "/name"})
_INDEX = re.compile(r"0|[1-9][0-9]*")


def valid_draft(
    document: JsonValue, diagnostics: Iterable[Diagnostic], graph_id: str | None
) -> JsonObject:
    """A copy of `document`, or `GraphInvalid` with the problems that keep it from a change."""
    problems = draft_problems(document, diagnostics, graph_id)
    if problems:
        raise GraphInvalid(problems)
    return json_object(document)


def same_document(first: JsonObject, second: JsonObject) -> bool:
    """Equal as compact JSON keeping key order, which is meaningful: a reorder is a change."""
    return _ordered_json(first) == _ordered_json(second)


def document_name(document: JsonObject) -> str:
    return str(document["name"])


def _ordered_json(document: JsonObject) -> str:
    return json.dumps(document, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def draft_problems(
    document: JsonValue, diagnostics: Iterable[Diagnostic], graph_id: str | None
) -> tuple[Diagnostic, ...]:
    """Errors that keep a draft from being stored: its type, size, format, `id` and `name`.

    Other diagnostics are allowed in a draft. With `graph_id`, the `id` must equal it.
    """
    found = [item for item in diagnostics if _blocks_draft(item)]
    if len(encode_json(document).encode("utf-8")) > MAX_DRAFT_BYTES:
        message = "The graph document is larger than 1 MiB."
        found.append(Diagnostic("error", "invalid_document", message, "", None))
    identifier = document.get("id") if isinstance(document, dict) else None
    if graph_id is not None and isinstance(identifier, str) and identifier != graph_id:
        message = f"The graph identifier must stay “{graph_id}”; it cannot change between versions."
        found.append(Diagnostic("error", "invalid_document", message, "/id", None))
    return tuple(sorted(found, key=_order))


def _blocks_draft(diagnostic: Diagnostic) -> bool:
    error = diagnostic.severity == "error" and diagnostic.code == "invalid_document"
    return error and diagnostic.path in _DRAFT_PATHS


def _order(diagnostic: Diagnostic) -> tuple[tuple[tuple[int, int, str], ...], str]:
    """By path, comparing array indices as numbers, then by code, like validation."""
    tokens = parse_pointer(diagnostic.path)
    order = tuple(
        (0, int(token), "") if _INDEX.fullmatch(token) else (1, 0, token) for token in tokens
    )
    return order, diagnostic.code
