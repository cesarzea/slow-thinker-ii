"""Real SQLite and transient authority exercise complete admission transactions."""

from dataclasses import dataclass
from pathlib import Path

from slow_thinker_ii.access import AccessPolicy, CallAuthority
from slow_thinker_ii.accounting import BudgetScope, ScopeKeys, ScopeKind
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteLedgerStore, SqliteRunStore
from slow_thinker_ii.application import ChargeBasis, RunAdmission, RunRecord

from .authority import Clock, authority

CHARGE = ChargeBasis(100, "tariff-revision", '{"currency":"USD","fixture":true}')


@dataclass(frozen=True)
class RunCase:
    database: SqliteDatabase
    store: SqliteRunStore
    service: RunAdmission
    authority: CallAuthority
    clock: Clock
    keys: ScopeKeys


def run_case(
    path: Path,
    *,
    limit: int = 4096,
    clock: Clock | None = None,
    seconds: float = 20,
    start: bool = True,
    policy: AccessPolicy | None = None,
    calls: int = 10,
    revision: str = "revision",
    snapshot_json: str = "{}",
) -> RunCase:
    clock = Clock() if clock is None else clock
    deadline = clock() + 90
    database = SqliteDatabase(path)
    database.initialize()
    keys = ScopeKeys("run", "session", "2026-09")
    create_scopes(database, keys)
    store = SqliteRunStore(database, limit, lambda: 1_790_553_600)
    with store.begin() as transaction:
        transaction.create_run(
            RunRecord("run", revision, "session", "2026-09", "runtime", deadline, snapshot_json)
        )
    grants = authority(
        clock, seconds=seconds, deadline=deadline, policy=policy, calls=calls, revision=revision
    )
    service = RunAdmission(grants, store, "run", "runtime", clock)
    if start:
        service.start()
    return RunCase(database, store, service, grants, clock, keys)


def outstanding(case: RunCase) -> tuple[int, ...]:
    with case.store.begin() as transaction:
        return tuple(scope.outstanding for scope in transaction.scopes(case.keys))


def create_scopes(database: SqliteDatabase, keys: ScopeKeys) -> None:
    ledger = SqliteLedgerStore(database)
    scopes: tuple[tuple[ScopeKind, str], ...] = (
        ("run", keys.run),
        ("session", keys.session),
        ("month", keys.month),
    )
    for kind, key in scopes:
        ledger.create_scope(BudgetScope(kind, key, 1000, 0, 0))
