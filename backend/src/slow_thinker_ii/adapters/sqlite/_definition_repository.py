"""Transactional append-only graph definition repository."""

import sqlite3

from slow_thinker_ii.application import library

from ._database import SqliteDatabase
from ._rows import integer, text


class SqliteDefinitionRepository:
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def read(self, reference: library.GraphReference) -> str | None:
        with self._database.transaction() as connection:
            row = connection.execute(
                "SELECT definition_json FROM personal_definitions WHERE graph_id=? AND revision=?",
                (reference.graph_id, reference.revision),
            ).fetchone()
        return None if row is None else text(row, "definition_json")

    def insert(self, document: library.ValidatedDefinition, parent_is_bundled: bool) -> bool:
        reference, parent = document.reference, document.parent
        with self._database.transaction() as connection:
            row = connection.execute(
                "SELECT definition_json FROM personal_definitions WHERE graph_id=? AND revision=?",
                (reference.graph_id, reference.revision),
            ).fetchone()
            if row is not None:
                if text(row, "definition_json") != document.definition_json:
                    raise library.DefinitionError("definition_conflict")
                return False
            if parent is not None:
                require_parent(connection, reference, parent, parent_is_bundled)
            connection.execute(
                "INSERT INTO personal_definitions (graph_id,revision,definition_json,"
                "parent_graph_id,parent_revision,parent_is_bundled) VALUES (?,?,?,?,?,?)",
                (
                    reference.graph_id,
                    reference.revision,
                    document.definition_json,
                    None if parent is None else parent.graph_id,
                    None if parent is None else parent.revision,
                    int(parent is not None and parent_is_bundled),
                ),
            )
        return True

    def page(self, after: int, through: int | None, limit: int) -> library.StoredDefinitionPage:
        require_page(after, through, limit)
        with self._database.transaction() as connection:
            if through is None:
                through = int(
                    connection.execute(
                        "SELECT COALESCE(MAX(sequence),0) FROM personal_definitions"
                    ).fetchone()[0]
                )
            rows = connection.execute(
                "SELECT sequence,definition_json FROM personal_definitions "
                "WHERE sequence>? AND sequence<=? ORDER BY sequence LIMIT ?",
                (after, through, limit + 1),
            ).fetchall()
        selected = rows[:limit]
        return library.StoredDefinitionPage(
            tuple(text(row, "definition_json") for row in selected),
            through,
            integer(selected[-1], "sequence") if selected else after,
            len(rows) > limit,
        )


def require_parent(
    connection: sqlite3.Connection,
    reference: library.GraphReference,
    parent: library.GraphReference,
    bundled: bool,
) -> None:
    if parent == reference:
        raise library.DefinitionError("invalid_definition")
    if (
        not bundled
        and connection.execute(
            "SELECT 1 FROM personal_definitions WHERE graph_id=? AND revision=?",
            (parent.graph_id, parent.revision),
        ).fetchone()
        is None
    ):
        raise library.DefinitionError("definition_parent_missing")


def require_page(after: int, through: int | None, limit: int) -> None:
    if type(after) is not int or type(limit) is not int or not 0 <= limit <= 100:
        raise ValueError("Invalid personal definition page")
    upper = 2**63 - 1 if through is None else through
    if type(upper) is not int or not 0 <= after <= upper <= 2**63 - 1:
        raise ValueError("Invalid personal definition page position")
