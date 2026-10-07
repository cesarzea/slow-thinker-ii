"""JSON Pointers (RFC 6901): parsing, formatting and lookup inside JSON values."""

import re
from collections.abc import Iterable

from ._json import JsonValue

_TOKEN = re.compile(r"(?:[^~]|~[01])*")
_INDEX = re.compile(r"0|[1-9][0-9]*")


def parse_pointer(pointer: str) -> tuple[str, ...]:
    """Split a pointer into unescaped reference tokens; the empty pointer has none."""
    if pointer == "":
        return ()
    if not pointer.startswith("/"):
        raise ValueError("A JSON Pointer must be empty or start with '/'")
    tokens = pointer[1:].split("/")
    if any(_TOKEN.fullmatch(token) is None for token in tokens):
        raise ValueError("A JSON Pointer contains an invalid '~' escape")
    return tuple(token.replace("~1", "/").replace("~0", "~") for token in tokens)


def format_pointer(tokens: Iterable[str | int]) -> str:
    """Join reference tokens, escaping '~' and '/'."""
    return "".join("/" + str(token).replace("~", "~0").replace("/", "~1") for token in tokens)


def value_at_pointer(value: JsonValue, tokens: Iterable[str | int]) -> JsonValue:
    """Return the referenced value, or None when the tokens do not resolve."""
    current = value
    for token in tokens:
        key = str(token)
        if isinstance(current, dict):
            current = current.get(key)
        elif isinstance(current, list) and _INDEX.fullmatch(key) and int(key) < len(current):
            current = current[int(key)]
        else:
            return None
    return current
