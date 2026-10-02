"""Immutable personal-definition boundary records."""

from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.definitions import GraphSummary


@dataclass(frozen=True)
class GraphReference:
    graph_id: str
    revision: str


@dataclass(frozen=True)
class DefinitionIssue:
    pointer: str
    message: str


class DefinitionError(ValueError):
    def __init__(self, code: str, issues: tuple[DefinitionIssue, ...] = ()) -> None:
        self.code, self.issues = code, issues
        super().__init__(code)


@dataclass(frozen=True)
class ValidatedDefinition:
    reference: GraphReference
    definition_json: str
    parent: GraphReference | None
    summary: GraphSummary


@dataclass(frozen=True)
class StoredDefinitionPage:
    definitions: tuple[str, ...]
    through: int
    last: int
    has_more: bool


@dataclass(frozen=True)
class LibraryItem:
    summary: GraphSummary
    origin: Literal["bundled", "personal"]
    parent: GraphReference | None


@dataclass(frozen=True)
class LibraryPage:
    items: tuple[LibraryItem, ...]
    next_cursor: str | None


@dataclass(frozen=True)
class SaveResult:
    reference: GraphReference
    created: bool
