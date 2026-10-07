"""The graph store port: branches of working-copy changes, and immutable versions."""

from datetime import datetime
from typing import Protocol

from slow_thinker_ii.contracts import JsonObject

from ._change_records import BranchSummary, ChangeRecord, ChangeSummary
from ._graph_records import GraphRecord, GraphSummary, VersionRecord


class GraphStore(Protocol):
    """Graphs as branches of working-copy changes, and immutable versions; change and version
    numbers are unique per graph. `branch` is a branch name; `name` is the document's name."""

    def create(self, graph_id: str, name: str, document: JsonObject, at: datetime) -> None:
        """Stores a new graph with branch `main` and its change 1; raises `GraphExists`."""
        ...

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
        """Adds a branch started from a version or a change, with its first change holding
        `document`; returns that change. Raises `BranchExists` for a name already used,
        ignoring case."""
        ...

    def add_change(
        self, graph_id: str, branch: str, name: str, document: JsonObject, at: datetime
    ) -> int:
        """Appends the graph's next change to an existing branch and returns its number."""
        ...

    def branches(self, graph_id: str) -> tuple[BranchSummary, ...]:
        """The graph's branches, oldest first; empty for an unknown graph."""
        ...

    def latest_change(self, graph_id: str, branch: str) -> ChangeRecord | None:
        """The branch's latest change; None for an unknown graph or branch."""
        ...

    def changes(
        self, graph_id: str, branch: str | None, before: int | None, limit: int
    ) -> tuple[ChangeSummary, ...]:
        """Changes of one branch (every branch when None) numbered below `before` (all when
        None), newest first, at most `limit`."""
        ...

    def change(self, graph_id: str, change: int) -> ChangeRecord | None: ...

    def add_version(self, graph_id: str, change: int, parent: int | None, at: datetime) -> int:
        """Creates the graph's next version from an existing change, on that change's branch,
        following `parent`; returns its number. The highest version is the active one."""
        ...

    def graphs(self) -> tuple[GraphSummary, ...]:
        """Every graph, the most recently changed first."""
        ...

    def graph(self, graph_id: str) -> GraphRecord | None:
        """Active version, latest change, branches and versions (oldest first) of a graph."""
        ...

    def version(self, graph_id: str, version: int) -> VersionRecord | None: ...
