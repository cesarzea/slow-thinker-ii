"""Located problems of a JSON value against a JSON Schema, in plain English."""

import re
from collections.abc import Sequence
from dataclasses import dataclass

from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json

from ._schemas import violations
from ._values import mapping, member, text

type Labels = Sequence[tuple[tuple[str, ...], str]]

_INDEX = re.compile(r"0|[1-9][0-9]*")
_PHRASES = (
    ("required", "is required"),
    ("type", "has the wrong type"),
    ("pattern", "has an invalid format"),
    ("maxLength", "is too long"),
    ("maxItems", "is too long"),
)


@dataclass(frozen=True)
class SchemaProblem:
    path: tuple[str, ...]  # JSON Pointer tokens of the offending value; missing members included
    keyword: str  # the failing keyword; empty for a `false` schema
    phrase: str  # for example "must be at most 128000"
    sentence: str  # for example "Max output tokens must be at most 128000."

    @staticmethod
    def label_of(path: tuple[str, ...], labels: Labels = (), fallback: str = "Value") -> str:
        """The label that sentences about the value at `path` start with.

        The deepest of `labels` whose path contains `path`; otherwise a readable form of its
        last property name (`output_format` becomes `Output format`); otherwise `fallback`.
        """
        matching = [(len(known), label) for known, label in labels if path[: len(known)] == known]
        if matching:
            return max(matching)[1]
        names = [token for token in path if _INDEX.fullmatch(token) is None]
        return _readable(names[-1]) if names else fallback


def schema_problems(
    schema: JsonObject, value: JsonValue, labels: Labels | None = None, fallback: str = "Value"
) -> tuple[SchemaProblem, ...]:
    """Distinct problems of `value` in validation order; empty when it is valid.

    Draft 2020-12 with ECMA-262 patterns; references are never fetched. Each sentence
    starts with `SchemaProblem.label_of(path, labels, fallback)`, where `labels` defaults
    to the `title` of each property of `schema`.
    """
    known = _titles(schema) if labels is None else labels
    found: list[SchemaProblem] = []
    seen: set[SchemaProblem] = set()
    for violation in violations(schema, value):
        phrase = _phrase(violation.keyword, violation.value)
        sentence = f"{SchemaProblem.label_of(violation.location, known, fallback)} {phrase}."
        problem = SchemaProblem(violation.location, violation.keyword, phrase, sentence)
        if problem not in seen:
            seen.add(problem)
            found.append(problem)
    return tuple(found)


def _titles(schema: JsonValue, prefix: tuple[str, ...] = ()) -> list[tuple[tuple[str, ...], str]]:
    """The `title` of each property, nested through `properties`."""
    found: list[tuple[tuple[str, ...], str]] = []
    for name, definition in mapping(member(schema, "properties")).items():
        title = text(member(definition, "title"))
        if title:
            found.append(((*prefix, name), title))
        found.extend(_titles(definition, (*prefix, name)))
    return found


def _readable(name: str) -> str:
    words = name.replace("_", " ").replace("-", " ").strip()
    return words[:1].upper() + words[1:] if words else "Value"


def _phrase(keyword: str, value: JsonValue) -> str:
    if keyword == "minLength" and value == 1:
        return "is required"
    if keyword == "enum":
        choices = value if isinstance(value, list) else [value]
        return "must be one of " + ", ".join(encode_json(choice) for choice in choices)
    if keyword in ("minimum", "maximum"):
        bound = "least" if keyword == "minimum" else "most"
        return f"must be at {bound} {encode_json(value)}"
    return next((phrase for name, phrase in _PHRASES if name == keyword), "is invalid")
