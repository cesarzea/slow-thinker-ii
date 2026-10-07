"""`GraphStore`: branches of each graph's working copy, their changes and activated versions.

Changes and versions are numbered per graph from 1 without gaps, across branches. Changes are
append-only; a version names its branch, its change and the version it follows (`parent`).
"""

from datetime import datetime

from slow_thinker_ii.application import (
    BranchSummary,
    ChangeRecord,
    ChangeSummary,
    GraphRecord,
    GraphSummary,
    VersionRecord,
)
from slow_thinker_ii.contracts import JsonObject

from ._database import SqliteDatabase
from ._graph_rows import (
    BRANCHES,
    CHANGES,
    SUMMARIES,
    VERSIONS,
    branch_summary,
    change_record,
    change_summary,
    graph_summary,
    version_summary,
)
from ._graph_writes import activate, append_change, create_branch, create_graph
from ._rows import integer, moment, optional_integer, stored_object, text


class SqliteGraphStore:
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def create(self, graph_id: str, name: str, document: JsonObject, at: datetime) -> None:
        """Stores a new graph with branch `main` and its change 1; raises `GraphExists`."""
        with self._database.transaction() as connection:
            create_graph(connection, graph_id, name, document, at)

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
        `document`; returns that change. Raises `BranchExists` for a name already used ignoring
        case, `GraphNotFound`."""
        start = (from_version, from_change)
        with self._database.transaction() as connection:
            return create_branch(connection, graph_id, branch, (name, document), start, at)

    def add_change(
        self, graph_id: str, branch: str, name: str, document: JsonObject, at: datetime
    ) -> int:
        """Appends the graph's next change to the branch; a document identical to the branch's
        latest change adds nothing and returns it. Raises `GraphNotFound`, `BranchNotFound`."""
        with self._database.transaction() as connection:
            return append_change(connection, graph_id, branch, (name, document), at)

    def branches(self, graph_id: str) -> tuple[BranchSummary, ...]:
        """The graph's branches, oldest first; empty for an unknown graph."""
        with self._database.transaction() as connection:
            rows = connection.execute(BRANCHES, (graph_id,)).fetchall()
        return tuple(branch_summary(row) for row in rows)

    def latest_change(self, graph_id: str, branch: str) -> ChangeRecord | None:
        with self._database.transaction() as connection:
            row = connection.execute(
                f"{CHANGES} WHERE c.graph_id = ? AND c.branch = ? ORDER BY c.change DESC LIMIT 1",
                (graph_id, branch),
            ).fetchone()
        return None if row is None else change_record(graph_id, row)

    def changes(
        self, graph_id: str, branch: str | None, before: int | None, limit: int
    ) -> tuple[ChangeSummary, ...]:
        """Changes of one branch (every branch when None) numbered below `before` (all when
        None), newest first, at most `limit`."""
        query = (
            f"{CHANGES} WHERE c.graph_id = ? AND (? IS NULL OR c.branch = ?) "
            "AND (? IS NULL OR c.change < ?) ORDER BY c.change DESC LIMIT ?"
        )
        values = (graph_id, branch, branch, before, before, max(limit, 0))
        with self._database.transaction() as connection:
            rows = connection.execute(query, values).fetchall()
        return tuple(change_summary(row) for row in rows)

    def change(self, graph_id: str, change: int) -> ChangeRecord | None:
        with self._database.transaction() as connection:
            row = connection.execute(
                f"{CHANGES} WHERE c.graph_id = ? AND c.change = ?", (graph_id, change)
            ).fetchone()
        return None if row is None else change_record(graph_id, row)

    def add_version(self, graph_id: str, change: int, parent: int | None, at: datetime) -> int:
        """Creates the graph's next version from the change, on its branch, following `parent`;
        raises `ChangeNotFound`. The highest version is the active one."""
        with self._database.transaction() as connection:
            return activate(connection, graph_id, change, parent, at)

    def graphs(self) -> tuple[GraphSummary, ...]:
        """Every graph, the most recently changed first."""
        with self._database.transaction() as connection:
            rows = connection.execute(f"{SUMMARIES} ORDER BY c.at DESC, g.rowid DESC").fetchall()
        return tuple(graph_summary(row) for row in rows)

    def graph(self, graph_id: str) -> GraphRecord | None:
        """Active version, latest change, branches and versions (oldest first) of a graph."""
        with self._database.transaction() as connection:
            row = connection.execute(f"{SUMMARIES} WHERE g.id = ?", (graph_id,)).fetchone()
            branches = connection.execute(BRANCHES, (graph_id,)).fetchall()
            versions = connection.execute(
                f"{VERSIONS} WHERE v.graph_id = ? ORDER BY v.version", (graph_id,)
            ).fetchall()
        if row is None:
            return None
        summary = graph_summary(row)
        listed = tuple(branch_summary(item) for item in branches)
        lineage = tuple(version_summary(item) for item in versions)
        active, latest = summary.active_version, summary.latest_change
        return GraphRecord(graph_id, summary.name, active, latest, listed, lineage)

    def version(self, graph_id: str, version: int) -> VersionRecord | None:
        with self._database.transaction() as connection:
            row = connection.execute(
                f"{VERSIONS} WHERE v.graph_id = ? AND v.version = ?", (graph_id, version)
            ).fetchone()
        if row is None:
            return None
        branch, parent = text(row, "branch"), optional_integer(row, "parent")
        change, created = integer(row, "change"), moment(row, "created_at")
        document = stored_object(row, "document_json")
        return VersionRecord(graph_id, version, branch, parent, change, created, document)
