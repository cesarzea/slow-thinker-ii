"""The interface labels that configuration messages start with."""

from collections.abc import Sequence

from slow_thinker_ii.catalog import ComponentDeclaration
from slow_thinker_ii.contracts import parse_pointer

from ._values import items, mapping, member, text

type Labels = Sequence[tuple[tuple[str, ...], str]]


def field_labels(declaration: ComponentDeclaration) -> Labels:
    """(configuration location, label) of every field in the declaration's interface."""
    sections = items(member(declaration.document.get("ui"), "sections"))
    fields = [mapping(field) for section in sections for field in items(member(section, "fields"))]
    return [(parse_pointer(text(field.get("path"))), text(field.get("label"))) for field in fields]
