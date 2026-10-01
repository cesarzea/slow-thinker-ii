"""Resolve SARIF descriptor IDs and indices without accepting contradictions."""

from ._shapes import index_value, objects, text_value
from ._types import CodeQLFailure


def descriptors(value: object, context: str) -> list[dict[str, object]]:
    entries = objects(value, context)
    identifiers = [text_value(item.get("id"), f"{context} ID") for item in entries]
    if len(set(identifiers)) != len(identifiers):
        raise CodeQLFailure(f"{context} IDs must be unique")
    return entries


def referenced_descriptor(
    reference: dict[str, object], entries: list[dict[str, object]], context: str
) -> dict[str, object]:
    identifier = text_value(reference["id"], f"{context} ID") if "id" in reference else None
    indexed = None
    if "index" in reference:
        indexed = entries[index_value(reference["index"], len(entries), f"{context} index")]
    if identifier is None:
        if indexed is None:
            raise CodeQLFailure(f"{context} has no descriptor reference")
        return indexed
    matches = [entry for entry in entries if entry.get("id") == identifier]
    if len(matches) != 1:
        raise CodeQLFailure(f"Unknown {context}: {identifier}")
    if indexed is not None and indexed != matches[0]:
        raise CodeQLFailure(f"{context} ID disagrees with its index")
    return matches[0]
