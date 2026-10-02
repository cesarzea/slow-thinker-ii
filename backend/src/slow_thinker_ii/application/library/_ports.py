"""Explicit definition-source, validation and append-only storage ports."""

from typing import Protocol

from slow_thinker_ii.definitions import GraphSummary

from ._records import GraphReference, StoredDefinitionPage, ValidatedDefinition


class DefinitionReader(Protocol):
    def definition(self, graph_id: str, revision: str) -> str: ...


class BundledSource(DefinitionReader, Protocol):
    def summaries(self) -> tuple[GraphSummary, ...]: ...


class DefinitionValidator(Protocol):
    def validate(self, source: str) -> ValidatedDefinition: ...
    def detail(self, source: str) -> str: ...


class DefinitionRepository(Protocol):
    def read(self, reference: GraphReference) -> str | None: ...
    def insert(self, document: ValidatedDefinition, parent_is_bundled: bool) -> bool: ...
    def page(self, after: int, through: int | None, limit: int) -> StoredDefinitionPage: ...
