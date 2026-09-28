"""Trusted preflight data and clocks exercise the real operator transaction boundary."""

from dataclasses import dataclass
from pathlib import Path

from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import (
    CommandReceipt,
    ExecutionConfiguration,
    LimitsProfile,
    PreparedStart,
    StartIntent,
)
from slow_thinker_ii.contracts import encode_json


@dataclass
class Clock:
    value: float

    def __call__(self) -> float:
        return self.value


@dataclass(frozen=True)
class OperatorCase:
    database: SqliteDatabase
    store: SqliteOperatorStore
    profile: ExecutionConfiguration
    clock: Clock
    wall: Clock
    session_id: str

    def prepared(self) -> PreparedStart:
        intent = StartIntent(
            self.session_id, "example", "v1", self.profile.revision, '{"p":"test"}'
        )
        return PreparedStart(intent, self.profile, "runtime", '{"validated":true}')


def operator_case(directory: Path) -> OperatorCase:
    database = SqliteDatabase(directory / "workspace.sqlite")
    database.initialize()
    clock, wall = Clock(100), Clock(1_790_553_600)
    store = SqliteOperatorStore(database, 1_048_576, clock, wall)
    profile = LimitsProfile("limits-1", 90, 20, 10, 5, 100, 8, 1_048_576, 1000, 5000, 10000)
    configuration = ExecutionConfiguration("configuration-1", profile, "{}")
    store.configure(configuration)
    receipt = store.create_session("create-session", "Research").receipt
    assert receipt.target_id is not None
    return OperatorCase(database, store, configuration, clock, wall, receipt.target_id)


def complete(case: OperatorCase, receipt: CommandReceipt, *, cleanup: bool = True) -> None:
    assert receipt.target_id is not None
    with SqliteRunStore(case.database, 1_048_576).begin() as transaction:
        transaction.start(receipt.target_id)
        transaction.finish_run(receipt.target_id, "runtime", case.clock(), "{}", executing=False)
        if cleanup:
            transaction.event(
                receipt.target_id,
                "run.cleanup",
                None,
                encode_json(
                    {
                        "pending_calls": [],
                        "environment_json": "[]",
                        "error_type": None,
                    }
                ),
            )
