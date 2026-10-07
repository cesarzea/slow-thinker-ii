"""The graph library: branches of working-copy changes, and versions activated from them."""

from collections.abc import Callable
from datetime import datetime

from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.graphs import Diagnostic, GraphInvalid, has_errors, validate_document

from ._branches import MAIN, checked_name, existing_branch, parent_of, start_document
from ._change_records import BranchSummary, ChangeRecord, ChangeSummary
from ._drafts import document_name, same_document, valid_draft
from ._errors import BranchExists, ChangeNotFound, GraphNotFound, VersionNotFound
from ._graph_records import GraphRecord, GraphSummary, VersionRecord, VersionSummary
from ._ports import Clock, GraphStore

MAX_CHANGES = 100


class GraphLibrary:
    def __init__(self, store: GraphStore, catalog: Callable[[], Catalog], clock: Clock) -> None:
        self._store = store
        self._catalog = catalog
        self._clock = clock

    def validate(self, document: JsonValue) -> tuple[Diagnostic, ...]:
        return validate_document(document, self._catalog())

    def create(self, document: JsonValue) -> tuple[str, str, int]:
        """Stores a new graph whose `main` branch starts with the draft: `(id, "main", 1)`."""
        source = valid_draft(document, self.validate(document), None)
        graph_id = str(source["id"])
        self._store.create(graph_id, document_name(source), source, self._clock.now())
        return graph_id, MAIN, 1

    def record_change(
        self, graph_id: str, branch: str, document: JsonValue
    ) -> tuple[int, datetime, bool]:
        """Appends the draft to a branch: `(change, at, True)`, or that branch's latest change
        with `False` when the document is identical to it."""
        existing_branch(self._store, graph_id, branch)
        source = valid_draft(document, self.validate(document), graph_id)
        latest = self._store.latest_change(graph_id, branch)
        if latest is not None and same_document(source, latest.document):
            return latest.change, latest.at, False
        at = self._clock.now()
        number = self._store.add_change(graph_id, branch, document_name(source), source, at)
        return number, at, True

    def create_branch(
        self,
        graph_id: str,
        name: str,
        *,
        from_version: int | None = None,
        from_change: int | None = None,
    ) -> int:
        """Starts a branch whose first change holds the document of one version or change."""
        document = start_document(self._store, graph_id, from_version, from_change)
        taken = {branch.name.lower() for branch in self._store.branches(graph_id)}
        if checked_name(name).lower() in taken:
            raise BranchExists(graph_id, name)
        at, title = self._clock.now(), document_name(document)
        return self._store.create_branch(
            graph_id, name, title, document, from_version, from_change, at
        )

    def branches(self, graph_id: str) -> tuple[BranchSummary, ...]:
        branches = self._store.branches(graph_id)
        if not branches:
            raise GraphNotFound(graph_id)
        return branches

    def changes(
        self, graph_id: str, branch: str | None = None, before: int | None = None, limit: int = 50
    ) -> tuple[ChangeSummary, ...]:
        """Changes of a branch, or of every branch, numbered below `before`, newest first."""
        existing_branch(self._store, graph_id, branch or MAIN)
        bounded = min(max(limit, 1), MAX_CHANGES)
        return self._store.changes(graph_id, branch, before, bounded)

    def change(self, graph_id: str, change: int) -> ChangeRecord:
        record = self._store.change(graph_id, change)
        if record is None:
            raise ChangeNotFound(graph_id, change)
        return record

    def activate(self, graph_id: str, change: int) -> VersionSummary:
        """Creates the next version on the change's branch, following that branch's head
        version (or the version it started from); it becomes the graph's active version."""
        record = self.change(graph_id, change)
        diagnostics = self.validate(record.document)
        if has_errors(diagnostics):
            raise GraphInvalid(diagnostics)
        parent = parent_of(existing_branch(self._store, graph_id, record.branch))
        at = self._clock.now()
        version = self._store.add_version(graph_id, change, parent, at)
        name = document_name(record.document)
        return VersionSummary(version, record.branch, parent, change, name, at)

    def graphs(self) -> tuple[GraphSummary, ...]:
        return self._store.graphs()

    def graph(self, graph_id: str) -> GraphRecord:
        record = self._store.graph(graph_id)
        if record is None:
            raise GraphNotFound(graph_id)
        return record

    def version(self, graph_id: str, version: int) -> VersionRecord:
        record = self._store.version(graph_id, version)
        if record is None:
            raise VersionNotFound(graph_id, version)
        return record
