"""Read-only experiment selection through an injected definition store."""

from typing import Protocol

from slow_thinker_ii.definitions import GraphSummary


class DefinitionStore(Protocol):
    def summaries(self) -> tuple[GraphSummary, ...]: ...


class ExperimentCatalog:
    def __init__(self, store: DefinitionStore) -> None:
        self._store = store

    def list_graphs(self) -> tuple[GraphSummary, ...]:
        return self._store.summaries()
