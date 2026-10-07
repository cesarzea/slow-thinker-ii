"""Queries of graphs, branches, changes and versions, and their rows as application records."""

import sqlite3

from slow_thinker_ii.application import (
    BranchSummary,
    ChangeRecord,
    ChangeSummary,
    GraphSummary,
    VersionSummary,
)

from ._rows import integer, moment, optional_integer, stored_object, text

CHANGES = (
    "SELECT c.change, c.branch, c.at, c.name, c.document_json, "
    "(SELECT max(v.version) FROM graph_versions v "
    "WHERE v.graph_id = c.graph_id AND v.change = c.change) AS version FROM graph_changes c"
)
SUMMARIES = (
    "SELECT g.id, c.name, c.change AS latest_change, c.at AS updated_at, "
    "(SELECT max(v.version) FROM graph_versions v WHERE v.graph_id = g.id) AS active_version "
    "FROM graphs g JOIN graph_changes c ON c.graph_id = g.id "
    "AND c.change = (SELECT max(change) FROM graph_changes WHERE graph_id = g.id)"
)
BRANCHES = (
    "SELECT b.name, b.created_at, b.from_version, b.from_change, "
    "(SELECT max(c.change) FROM graph_changes c "
    "WHERE c.graph_id = b.graph_id AND c.branch = b.name) AS latest_change, "
    "(SELECT max(v.version) FROM graph_versions v "
    "WHERE v.graph_id = b.graph_id AND v.branch = b.name) AS head_version "
    "FROM graph_branches b WHERE b.graph_id = ? ORDER BY b.created_at, b.rowid"
)
VERSIONS = (
    "SELECT v.version, v.branch, v.parent, v.change, v.created_at, c.name, c.document_json "
    "FROM graph_versions v JOIN graph_changes c ON c.graph_id = v.graph_id AND c.change = v.change"
)


def change_record(graph_id: str, row: sqlite3.Row) -> ChangeRecord:
    number, branch, at = integer(row, "change"), text(row, "branch"), moment(row, "at")
    document, version = stored_object(row, "document_json"), optional_integer(row, "version")
    return ChangeRecord(graph_id, number, branch, at, document, version)


def change_summary(row: sqlite3.Row) -> ChangeSummary:
    number, branch, at = integer(row, "change"), text(row, "branch"), moment(row, "at")
    return ChangeSummary(number, branch, at, text(row, "name"), optional_integer(row, "version"))


def branch_summary(row: sqlite3.Row) -> BranchSummary:
    return BranchSummary(
        text(row, "name"),
        moment(row, "created_at"),
        optional_integer(row, "from_version"),
        optional_integer(row, "from_change"),
        integer(row, "latest_change"),
        optional_integer(row, "head_version"),
    )


def graph_summary(row: sqlite3.Row) -> GraphSummary:
    return GraphSummary(
        text(row, "id"),
        text(row, "name"),
        optional_integer(row, "active_version"),
        integer(row, "latest_change"),
        moment(row, "updated_at"),
    )


def version_summary(row: sqlite3.Row) -> VersionSummary:
    return VersionSummary(
        integer(row, "version"),
        text(row, "branch"),
        optional_integer(row, "parent"),
        integer(row, "change"),
        text(row, "name"),
        moment(row, "created_at"),
    )
