"""Writes of graphs, branches, changes and versions inside the caller's immediate transaction.

Change and version numbers are the graph's highest plus one, read in the same transaction as
the insert, so they stay unique and gap-free per graph across branches.
"""

import sqlite3
from datetime import datetime

from slow_thinker_ii.application import (
    BranchExists,
    BranchNotFound,
    ChangeNotFound,
    GraphExists,
    GraphNotFound,
)
from slow_thinker_ii.contracts import JsonObject

from ._graph_rows import CHANGES
from ._rows import dump, integer, stamp, text

MAIN = "main"
INSERT_CHANGE = (
    "INSERT INTO graph_changes (graph_id, change, branch, at, name, document_json) "
    "VALUES (?, ?, ?, ?, ?, ?)"
)
INSERT_BRANCH = (
    "INSERT INTO graph_branches (graph_id, name, folded, created_at, from_version, from_change) "
    "VALUES (?, ?, ?, ?, ?, ?)"
)
NEXT_CHANGE = "SELECT coalesce(max(change), 0) + 1 AS next FROM graph_changes WHERE graph_id = ?"
NEXT_VERSION = "SELECT coalesce(max(version), 0) + 1 AS next FROM graph_versions WHERE graph_id = ?"


def create_graph(
    connection: sqlite3.Connection, graph_id: str, name: str, document: JsonObject, at: datetime
) -> None:
    if _exists(connection, graph_id):
        raise GraphExists(graph_id)
    connection.execute("INSERT INTO graphs (id, created_at) VALUES (?, ?)", (graph_id, stamp(at)))
    connection.execute(INSERT_BRANCH, (graph_id, MAIN, MAIN.casefold(), stamp(at), None, None))
    connection.execute(INSERT_CHANGE, (graph_id, 1, MAIN, stamp(at), name, dump(document)))


def create_branch(
    connection: sqlite3.Connection,
    graph_id: str,
    branch: str,
    change: tuple[str, JsonObject],
    start: tuple[int | None, int | None],
    at: datetime,
) -> int:
    """Adds the branch, unique per graph ignoring case, and its first change; returns it."""
    if not _exists(connection, graph_id):
        raise GraphNotFound(graph_id)
    taken = connection.execute(
        "SELECT 1 FROM graph_branches WHERE graph_id = ? AND folded = ?",
        (graph_id, branch.casefold()),
    ).fetchone()
    if taken is not None:
        raise BranchExists(graph_id, branch)
    values = (graph_id, branch, branch.casefold(), stamp(at), *start)
    connection.execute(INSERT_BRANCH, values)
    return _insert_change(connection, graph_id, branch, change, at)


def append_change(
    connection: sqlite3.Connection,
    graph_id: str,
    branch: str,
    change: tuple[str, JsonObject],
    at: datetime,
) -> int:
    """Appends the graph's next change to the branch, unless the document is identical to the
    branch's latest one (stored JSON, keys in their order): then that change is returned."""
    latest = connection.execute(
        f"{CHANGES} WHERE c.graph_id = ? AND c.branch = ? ORDER BY c.change DESC LIMIT 1",
        (graph_id, branch),
    ).fetchone()
    if latest is None:
        if _exists(connection, graph_id):
            raise BranchNotFound(graph_id, branch)
        raise GraphNotFound(graph_id)
    if text(latest, "document_json") == dump(change[1]):
        return integer(latest, "change")
    return _insert_change(connection, graph_id, branch, change, at)


def activate(
    connection: sqlite3.Connection, graph_id: str, change: int, parent: int | None, at: datetime
) -> int:
    """Creates the graph's next version from the change, on its branch, following `parent`."""
    found = connection.execute(
        "SELECT branch FROM graph_changes WHERE graph_id = ? AND change = ?", (graph_id, change)
    ).fetchone()
    if found is None:
        raise ChangeNotFound(graph_id, change)
    number = _next(connection, NEXT_VERSION, graph_id)
    connection.execute(
        "INSERT INTO graph_versions (graph_id, version, branch, parent, change, created_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (graph_id, number, text(found, "branch"), parent, change, stamp(at)),
    )
    return number


def _insert_change(
    connection: sqlite3.Connection,
    graph_id: str,
    branch: str,
    change: tuple[str, JsonObject],
    at: datetime,
) -> int:
    number = _next(connection, NEXT_CHANGE, graph_id)
    name, document = change
    values = (graph_id, number, branch, stamp(at), name, dump(document))
    connection.execute(INSERT_CHANGE, values)
    return number


def _next(connection: sqlite3.Connection, query: str, graph_id: str) -> int:
    return integer(connection.execute(query, (graph_id,)).fetchone(), "next")


def _exists(connection: sqlite3.Connection, graph_id: str) -> bool:
    found = connection.execute("SELECT 1 FROM graphs WHERE id = ?", (graph_id,)).fetchone()
    return found is not None
