"""Read-only experiment selection through an injected definition store."""

from typing import Protocol

from slow_thinker_ii.definitions import GraphSummary


class DefinitionStore(Protocol):
    def summaries(self) -> tuple[GraphSummary, ...]: ...
    def detail(self, graph_id: str, revision: str) -> str: ...


class ExperimentCatalog:
    def __init__(self, store: DefinitionStore) -> None:
        self._store = store

    def list_graphs(self) -> tuple[GraphSummary, ...]:
        return self._store.summaries()

    def graph(self, graph_id: str, revision: str) -> str:
        return self._store.detail(graph_id, revision)
