"""Diagnostics of graph validation, in path order."""

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.contracts import JsonObject, parse_pointer

from ._values import INDEX


@dataclass(frozen=True)
class Diagnostic:
    severity: Literal["error", "warning"]
    code: str
    message: str
    path: str
    node_id: str | None

    def document(self) -> JsonObject:
        return {
            "severity": self.severity,
            "code": self.code,
            "message": self.message,
            "path": self.path,
            "node_id": self.node_id,
        }


class GraphInvalid(ValueError):
    """A graph document with errors; `diagnostics` holds its complete validation result."""

    def __init__(self, diagnostics: Iterable[Diagnostic]) -> None:
        self.diagnostics = tuple(diagnostics)
        errors = [item.message for item in self.diagnostics if item.severity == "error"]
        super().__init__(f"The graph has {len(errors)} error(s): {' '.join(errors)}")


def error(code: str, message: str, path: str, node_id: str | None = None) -> Diagnostic:
    return Diagnostic("error", code, message, path, node_id)


def warning(code: str, message: str, path: str, node_id: str | None = None) -> Diagnostic:
    return Diagnostic("warning", code, message, path, node_id)


def has_errors(diagnostics: Iterable[Diagnostic]) -> bool:
    return any(diagnostic.severity == "error" for diagnostic in diagnostics)


def in_path_order(diagnostics: Iterable[Diagnostic]) -> tuple[Diagnostic, ...]:
    """Distinct diagnostics sorted by path, with array indices compared as numbers, then code."""
    seen: set[Diagnostic] = set()
    distinct: list[Diagnostic] = []
    for diagnostic in diagnostics:
        if diagnostic not in seen:
            seen.add(diagnostic)
            distinct.append(diagnostic)
    return tuple(sorted(distinct, key=_order))


def _order(diagnostic: Diagnostic) -> tuple[tuple[tuple[int, int, str], ...], str]:
    tokens = parse_pointer(diagnostic.path)
    return tuple(_token_order(token) for token in tokens), diagnostic.code


def _token_order(token: str) -> tuple[int, int, str]:
    return (0, int(token), "") if INDEX.fullmatch(token) else (1, 0, token)
