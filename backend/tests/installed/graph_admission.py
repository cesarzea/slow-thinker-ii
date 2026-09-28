"""Installed graph checks enter through the production command and session transaction."""

from pathlib import Path

from slow_thinker_ii.access import CallAuthority, CallLimits
from slow_thinker_ii.accounting import ScopeKeys
from slow_thinker_ii.adapters.catalog import InstalledPlan
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import (
    ExecutionConfiguration,
    LimitsProfile,
    PreparedStart,
    RunAdmission,
    RunRecord,
    StartIntent,
    sequence_access,
)
from support.managed_calls import RealClock
from support.run_admission import RunCase


def admission(directory: Path, installed: InstalledPlan) -> RunCase:
    database, clock = SqliteDatabase(directory / "run.sqlite"), RealClock()
    database.initialize()
    operator = SqliteOperatorStore(database, 1_048_576, clock)
    configuration = fixture_configuration(installed.plan.limits_profile)
    limits = configuration.limits
    operator.configure(configuration)
    session = operator.create_session("session", "Installed graph").receipt.target_id
    assert session is not None
    prepared = prepared_graph(installed, configuration, session)
    receipt = operator.admit("start", prepared).receipt
    assert receipt.target_id is not None and receipt.disposition == "accepted"
    assert operator.admit("start", prepared).replayed
    store = SqliteRunStore(database, limits.max_payload_bytes)
    with store.begin() as transaction:
        run = transaction.run(receipt.target_id)
    return runtime_case(database, store, installed, run, limits, clock)


def runtime_case(
    database: SqliteDatabase,
    store: SqliteRunStore,
    installed: InstalledPlan,
    run: RunRecord,
    limits: LimitsProfile,
    clock: RealClock,
) -> RunCase:
    authority = CallAuthority(
        run.run_id,
        run.graph_revision,
        sequence_access(installed.plan),
        CallLimits(limits.max_calls, limits.max_depth, limits.call_seconds),
        run.deadline,
        clock,
    )
    service = RunAdmission(authority, store, run.run_id, run.runtime_id, clock)
    return RunCase(
        database,
        store,
        service,
        authority,
        clock,
        ScopeKeys(run.run_id, run.session_id, run.month_id),
    )


def fixture_configuration(revision: str) -> ExecutionConfiguration:
    limits = LimitsProfile(
        revision,
        90,
        20,
        30,
        10,
        100,
        8,
        1_048_576,
        1_000_000_000,
        1_000_000_000,
        1_000_000_000,
    )
    return ExecutionConfiguration("installed-fixture", limits, "{}")


def prepared_graph(
    installed: InstalledPlan, configuration: ExecutionConfiguration, session: str
) -> PreparedStart:
    intent = StartIntent(
        session,
        installed.plan.graph_id,
        installed.plan.revision,
        configuration.revision,
        installed.plan.input_json,
    )
    return PreparedStart(intent, configuration, "runtime", installed.plan.graph_json)
