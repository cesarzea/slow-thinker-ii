"""Atomic edits of unsaved source without a browser numeric round trip."""

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json, json_object

from ._errors import WorkspaceError
from ._pointer import edit


def patch_definition(source: str, operations: list[JsonObject], limit: int) -> str:
    try:
        if not operations or len(operations) > 128 or len(source.encode("utf-8")) > limit:
            raise WorkspaceError("invalid_patch")
        value = json_object(decode_json(source))
        for operation in operations:
            value = _apply(value, operation)
        result = encode_json(value)
        if len(result.encode("utf-8")) > limit:
            raise WorkspaceError("response_too_large")
        return result
    except WorkspaceError:
        raise
    except (ValueError, KeyError, IndexError, RecursionError, UnicodeError) as error:
        raise WorkspaceError("invalid_patch") from error


def _apply(value: JsonObject, operation: JsonObject) -> JsonObject:
    name, path, replacement = _operation(operation)
    if path == "":
        if name == "remove":
            raise WorkspaceError("invalid_patch")
        return json_object(replacement)
    edit(value, name, path, replacement)
    return value


def _operation(value: JsonObject) -> tuple[str, str, JsonValue]:
    name, path = value.get("op"), value.get("path")
    if name not in ("add", "replace", "remove") or not isinstance(path, str):
        raise WorkspaceError("invalid_patch")
    expected = {"op", "path"} if name == "remove" else {"op", "path", "value_json"}
    if set(value) != expected:
        raise WorkspaceError("invalid_patch")
    raw = value.get("value_json")
    if name != "remove" and not isinstance(raw, str):
        raise WorkspaceError("invalid_patch")
    replacement = None if name == "remove" else decode_json(str(raw))
    return str(name), path, replacement
