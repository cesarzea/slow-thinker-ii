"""Bounded diagnostics expose paths and fixed messages rather than source values."""

from collections.abc import Iterable
from typing import NoReturn

from slow_thinker_ii.application import library


def pointer(parts: Iterable[str | int]) -> str:
    value = "".join("/" + str(part).replace("~", "~0").replace("/", "~1") for part in parts)
    return value if len(value) <= 160 else ""


def reject(path: str, message: str) -> NoReturn:
    raise library.DefinitionError("invalid_definition", (library.DefinitionIssue(path, message),))


def require(condition: bool, path: str, message: str) -> None:
    if not condition:
        reject(path, message)
