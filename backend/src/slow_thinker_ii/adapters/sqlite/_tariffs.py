"""Append immutable tariff revisions and keep refresh outcomes across restarts."""

from pydantic import TypeAdapter

from slow_thinker_ii.accounting import RefreshStatus, Tariff, TariffRevision

from ._database import SqliteDatabase
from ._rows import integer, text

TARIFF_ADAPTER = TypeAdapter(Tariff)


class SqliteTariffStore:
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def status(self) -> RefreshStatus:
        with self._database.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM tariff_refresh ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
            success = connection.execute(
                "SELECT * FROM tariff_refresh WHERE error IS NULL ORDER BY sequence DESC LIMIT 1"
            ).fetchone()
        return RefreshStatus(
            None if row is None else integer(row, "attempted_at"),
            None if success is None else integer(success, "attempted_at"),
            None if success is None else text(success, "digest"),
            None if row is None or row["error"] is None else text(row, "error"),
        )

    def publish(self, revision: TariffRevision) -> None:
        with self._database.transaction() as connection:
            connection.execute(
                "INSERT INTO tariff_revisions VALUES (?,?,?,?,?) ON CONFLICT(digest) DO NOTHING",
                (
                    revision.digest,
                    revision.retrieved_at,
                    revision.source,
                    TARIFF_ADAPTER.dump_json(revision.tariff).decode(),
                    revision.source_json,
                ),
            )
            connection.execute(
                "INSERT INTO tariff_refresh(attempted_at,digest) VALUES (?,?)",
                (revision.retrieved_at, revision.digest),
            )

    def failed(self, now: int, error: str) -> None:
        with self._database.transaction() as connection:
            connection.execute(
                "INSERT INTO tariff_refresh(attempted_at,error) VALUES (?,?)", (now, error)
            )

    def revision(self, digest: str) -> TariffRevision:
        with self._database.transaction() as connection:
            row = connection.execute(
                "SELECT * FROM tariff_revisions WHERE digest=?", (digest,)
            ).fetchone()
        if row is None:
            raise ValueError("Unknown tariff revision")
        return TariffRevision(
            text(row, "digest"),
            integer(row, "retrieved_at"),
            text(row, "source"),
            TARIFF_ADAPTER.validate_json(text(row, "tariff_json")),
            text(row, "source_json"),
        )
