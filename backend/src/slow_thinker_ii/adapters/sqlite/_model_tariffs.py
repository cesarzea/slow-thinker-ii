"""Independent immutable price histories for each reviewed direct billing profile."""

from slow_thinker_ii.accounting import RefreshStatus, TariffRevision
from slow_thinker_ii.application import workspace

from ._database import SqliteDatabase
from ._rows import integer, text
from ._tariffs import TARIFF_ADAPTER, SqliteTariffStore

OPENAI_PROFILE = "openai.gpt-6-luna.standard.text.v1"


class SqliteModelTariffStore:
    def __init__(self, database: SqliteDatabase, profile_id: str) -> None:
        if not profile_id or profile_id == OPENAI_PROFILE:
            raise ValueError("Use the legacy store for the reviewed OpenAI profile")
        self._database, self._profile = database, profile_id

    def status(self) -> RefreshStatus:
        with self._database.transaction() as db:
            row = db.execute(
                "SELECT * FROM model_tariff_refresh WHERE profile_id=? "
                "ORDER BY sequence DESC LIMIT 1",
                (self._profile,),
            ).fetchone()
            success = db.execute(
                "SELECT * FROM model_tariff_refresh WHERE profile_id=? "
                "AND error IS NULL ORDER BY sequence DESC LIMIT 1",
                (self._profile,),
            ).fetchone()
        return RefreshStatus(
            None if row is None else integer(row, "attempted_at"),
            None if success is None else integer(success, "attempted_at"),
            None if success is None else text(success, "digest"),
            None if row is None or row["error"] is None else text(row, "error"),
        )

    def publish(self, revision: TariffRevision) -> None:
        if revision.tariff.profile != self._profile:
            raise ValueError("Tariff does not match its reviewed billing profile")
        with self._database.transaction() as db:
            db.execute(
                "INSERT INTO model_tariff_revisions VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(profile_id,digest) DO NOTHING",
                (
                    self._profile,
                    revision.digest,
                    revision.retrieved_at,
                    revision.source,
                    TARIFF_ADAPTER.dump_json(revision.tariff).decode(),
                    revision.source_json,
                ),
            )
            db.execute(
                "INSERT INTO model_tariff_refresh(profile_id,attempted_at,digest) VALUES(?,?,?)",
                (self._profile, revision.retrieved_at, revision.digest),
            )

    def failed(self, now: int, error: str) -> None:
        with self._database.transaction() as db:
            db.execute(
                "INSERT INTO model_tariff_refresh(profile_id,attempted_at,error) VALUES(?,?,?)",
                (self._profile, now, error),
            )

    def revision(self, digest: str) -> TariffRevision:
        with self._database.transaction() as db:
            row = db.execute(
                "SELECT * FROM model_tariff_revisions WHERE profile_id=? AND digest=?",
                (self._profile, digest),
            ).fetchone()
        if row is None:
            raise ValueError("Unknown model tariff revision")
        return TariffRevision(
            text(row, "digest"),
            integer(row, "retrieved_at"),
            text(row, "source"),
            TARIFF_ADAPTER.validate_json(text(row, "tariff_json")),
            text(row, "source_json"),
        )


class SqliteModelTariffReader:
    def __init__(self, database: SqliteDatabase) -> None:
        self._database = database

    def selected(self, profile_id: str) -> workspace.ModelTariffSelection | None:
        store = (
            SqliteTariffStore(self._database)
            if profile_id == OPENAI_PROFILE
            else SqliteModelTariffStore(self._database, profile_id)
        )
        status = store.status()
        if status.revision is None or status.last_success is None:
            return None
        return workspace.ModelTariffSelection(store.revision(status.revision), status.last_success)
