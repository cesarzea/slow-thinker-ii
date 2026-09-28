"""JSON Pointer reads are data access, never expressions or silent fallback values."""

import re

from slow_thinker_ii.contracts import JsonValue


def pointer_tokens(pointer: str) -> tuple[str, ...]:
    if re.fullmatch(r"(?:/(?:[^~/]|~[01])*)*", pointer) is None:
        raise ValueError("Invalid JSON Pointer")
    if not pointer:
        return ()
    return tuple(part.replace("~1", "/").replace("~0", "~") for part in pointer[1:].split("/"))


def read_pointer(value: JsonValue, pointer: str) -> JsonValue:
    for token in pointer_tokens(pointer):
        if isinstance(value, dict) and token in value:
            value = value[token]
        elif isinstance(value, list) and re.fullmatch(r"0|[1-9][0-9]*", token):
            index = int(token)
            if index >= len(value):
                raise ValueError("JSON Pointer index is outside the array")
            value = value[index]
        else:
            raise ValueError("JSON Pointer does not identify an existing value")
    return value
