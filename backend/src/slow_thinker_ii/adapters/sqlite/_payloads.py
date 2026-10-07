"""The recording contract's payload bound: oversized payload-like fields become a preview.

Only the payload-like fields of an event's data are bounded; every other field (usage, amounts,
statuses, identifiers) is kept intact, because totals and recovery are computed from them.
"""

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._rows import dump

PAYLOAD_FIELDS = frozenset(
    {"payload", "input", "arguments", "result", "request", "response", "content"}
)
PREVIEW_BYTES = 4096


def bounded(data: JsonObject, max_bytes: int) -> JsonObject:
    """A copy of `data` whose payload-like fields serialize to at most `max_bytes` each."""
    return {
        key: _bounded(item, max_bytes) if key in PAYLOAD_FIELDS else item
        for key, item in data.items()
    }


def _bounded(value: JsonValue, max_bytes: int) -> JsonValue:
    """`{"truncated": true, "bytes": <size>, "preview": <first 4 KiB as text>}` when too large."""
    serialized = dump(value).encode("utf-8")
    if len(serialized) <= max_bytes:
        return value
    preview = serialized[:PREVIEW_BYTES].decode("utf-8", errors="ignore")
    return {"truncated": True, "bytes": len(serialized), "preview": preview}
