"""An in-memory `application.GraphStore`: branches of working-copy changes, and versions."""

from datetime import datetime

from slow_thinker_ii.application import (
    BranchExists,
    BranchSummary,
    ChangeRecord,
    ChangeSummary,
    GraphExists,
    GraphRecord,
    GraphSummary,
    VersionRecord,
)
from slow_thinker_ii.contracts import JsonObject, json_object

from .graph_rows import StoredBranch, StoredChange, StoredGraph, StoredVersion


class MemoryGraphStore:
    """`GraphStore` fake: change and version numbers per graph from 1; documents are copied
    in and out with their key order; branch names are unique ignoring case."""

    def __init__(self) -> None:
        self._graphs: dict[str, StoredGraph] = {}

    def create(self, graph_id: str, name: str, document: JsonObject, at: datetime) -> None:
        if graph_id in self._graphs:
            raise GraphExists(graph_id)
        change = StoredChange("main", name, at, json_object(document))
        self._graphs[graph_id] = StoredGraph([change], [StoredBranch("main", at, None, None)])

    def create_branch(
        self,
        graph_id: str,
        branch: str,
        name: str,
        document: JsonObject,
        from_version: int | None,
        from_change: int | None,
        at: datetime,
    ) -> int:
        graph = self._graphs[graph_id]
        if any(item.name.lower() == branch.lower() for item in graph.branches):
            raise BranchExists(graph_id, branch)
        graph.branches.append(StoredBranch(branch, at, from_version, from_change))
        return self.add_change(graph_id, branch, name, document, at)

    def add_change(
        self, graph_id: str, branch: str, name: str, document: JsonObject, at: datetime
    ) -> int:
        changes = self._graphs[graph_id].changes
        changes.append(StoredChange(branch, name, at, json_object(document)))
        return len(changes)

    def branches(self, graph_id: str) -> tuple[BranchSummary, ...]:
        graph = self._graphs.get(graph_id)
        return () if graph is None else tuple(map(graph.branch_summary, graph.branches))

    def latest_change(self, graph_id: str, branch: str) -> ChangeRecord | None:
        graph = self._graphs.get(graph_id)
        numbers = [] if graph is None else graph.numbers(branch)
        return self.change(graph_id, numbers[-1]) if numbers else None

    def changes(
        self, graph_id: str, branch: str | None, before: int | None, limit: int
    ) -> tuple[ChangeSummary, ...]:
        graph = self._graphs[graph_id]
        numbers = [n for n in graph.numbers(branch) if before is None or n < before]
        return tuple(graph.change_summary(n) for n in reversed(numbers[-limit:]))

    def change(self, graph_id: str, change: int) -> ChangeRecord | None:
        graph = self._graphs.get(graph_id)
        if graph is None or not 1 <= change <= len(graph.changes):
            return None
        item = graph.changes[change - 1]
        document, version = json_object(item.document), graph.version_of(change)
        return ChangeRecord(graph_id, change, item.branch, item.at, document, version)

    def add_version(self, graph_id: str, change: int, parent: int | None, at: datetime) -> int:
        versions = self._graphs[graph_id].versions
        versions.append(StoredVersion(change, parent, at))
        return len(versions)

    def graphs(self) -> tuple[GraphSummary, ...]:
        summaries = [_summary(graph_id, graph) for graph_id, graph in self._graphs.items()]
        return tuple(sorted(summaries, key=lambda summary: summary.updated_at, reverse=True))

    def graph(self, graph_id: str) -> GraphRecord | None:
        graph = self._graphs.get(graph_id)
        if graph is None:
            return None
        summary = _summary(graph_id, graph)
        branches = tuple(map(graph.branch_summary, graph.branches))
        versions = tuple(map(graph.version_summary, range(1, len(graph.versions) + 1)))
        active, latest = summary.active_version, summary.latest_change
        return GraphRecord(graph_id, summary.name, active, latest, branches, versions)

    def version(self, graph_id: str, version: int) -> VersionRecord | None:
        graph = self._graphs.get(graph_id)
        if graph is None or not 1 <= version <= len(graph.versions):
            return None
        item = graph.version_summary(version)
        document = json_object(graph.changes[item.change - 1].document)
        branch, parent, change, at = item.branch, item.parent, item.change, item.created_at
        return VersionRecord(graph_id, version, branch, parent, change, at, document)


def _summary(graph_id: str, graph: StoredGraph) -> GraphSummary:
    latest = graph.changes[-1]
    active = len(graph.versions) or None
    return GraphSummary(graph_id, latest.name, active, len(graph.changes), latest.at)
