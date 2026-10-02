"""Strict JSON Pointer object/array edit semantics."""

import re

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._errors import WorkspaceError


def parts(path: str) -> list[str]:
    if not path.startswith("/") or len(path) > 4096:
        raise WorkspaceError("invalid_patch")
    tokens = path[1:].split("/")
    if len(tokens) > 64 or any(re.search(r"~(?![01])", token) for token in tokens):
        raise WorkspaceError("invalid_patch")
    return [token.replace("~1", "/").replace("~0", "~") for token in tokens]


def index(key: str, size: int, *, insertion: bool = False) -> int:
    if insertion and key == "-":
        return size
    if not re.fullmatch(r"0|[1-9][0-9]{0,9}", key):
        raise WorkspaceError("invalid_patch")
    position = int(key)
    if position >= size + int(insertion):
        raise WorkspaceError("invalid_patch")
    return position


def edit(value: JsonObject, name: str, path: str, replacement: JsonValue) -> None:
    keys = parts(path)
    parent: JsonValue = value
    for key in keys[:-1]:
        if isinstance(parent, dict):
            parent = parent[key]
        elif isinstance(parent, list):
            parent = parent[index(key, len(parent))]
        else:
            raise WorkspaceError("invalid_patch")
    key = keys[-1]
    if isinstance(parent, dict):
        _object(parent, key, name, replacement)
    elif isinstance(parent, list):
        _array(parent, key, name, replacement)
    else:
        raise WorkspaceError("invalid_patch")


def _object(parent: JsonObject, key: str, name: str, replacement: JsonValue) -> None:
    if name != "add" and key not in parent:
        raise WorkspaceError("invalid_patch")
    if name == "remove":
        del parent[key]
    else:
        parent[key] = replacement


def _array(parent: list[JsonValue], key: str, name: str, replacement: JsonValue) -> None:
    position = index(key, len(parent), insertion=name == "add")
    if name == "add":
        parent.insert(position, replacement)
    elif name == "remove":
        parent.pop(position)
    else:
        parent[position] = replacement
