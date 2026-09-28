"""Limits remain exact, frozen per run, and shared budgets retain all existing obligations."""

from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteOperatorStore, SqliteRunStore
from slow_thinker_ii.application import ExecutionConfiguration
from slow_thinker_ii.contracts import decode_json, json_object
from support.operator_commands import complete, operator_case


def test_no_configuration_rejection_is_durable(tmp_path: Path) -> None:
    db = SqliteDatabase(tmp_path / "empty.sqlite")
    db.initialize()
    store = SqliteOperatorStore(db, 4096)
    assert store.profile() is None
    rejected = store.create_session("session", "Research")
    assert rejected.receipt.reason == "no_configuration"
    assert store.create_session("session", "Research").replayed


def test_configuration_changes_preserve_commitments_and_run_caps(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    receipt = case.store.admit("start", case.prepared()).receipt
    with case.database.transaction() as db:
        db.execute("UPDATE budget_scopes SET settled=17,reserved=23 WHERE kind!='run'")
    newer = changed_profile(case.profile)
    case.store.configure(newer)
    assert case.store.profile() == newer
    with case.database.transaction() as db:
        assert tuple(
            db.execute(
                "SELECT cap,settled,reserved FROM budget_scopes WHERE kind='session'"
            ).fetchone()
        ) == (50, 17, 23)
        assert db.execute("SELECT cap FROM budget_scopes WHERE kind='run'").fetchone()[0] == 1000
    with SqliteRunStore(case.database, 1_048_576).begin() as transaction:
        assert receipt.target_id is not None
        snapshot = json_object(decode_json(transaction.run(receipt.target_id).snapshot_json))
        assert snapshot["configuration"] == decode_json(case.profile.to_json())
    assert case.store.admit("stale", case.prepared()).receipt.reason == "configuration_changed"


def changed_profile(current: ExecutionConfiguration) -> ExecutionConfiguration:
    return replace(
        current,
        revision="configuration-2",
        limits=replace(
            current.limits,
            revision="limits-2",
            run_budget=200,
            session_budget=50,
            month_budget=60,
        ),
    )


def test_configuration_updates_reject_changed_revisions_and_insufficient_caps(
    tmp_path: Path,
) -> None:
    case = operator_case(tmp_path)
    with case.database.transaction() as db:
        db.execute("UPDATE budget_scopes SET settled=17,reserved=23")
    newer = changed_profile(case.profile)
    case.store.configure(newer)
    with pytest.raises(ValueError, match="immutable"):
        case.store.configure(replace(newer, limits=replace(newer.limits, month_budget=99)))
    with pytest.raises(ValueError, match="commitments"):
        case.store.configure(
            replace(newer, revision="invalid", limits=replace(newer.limits, session_budget=39))
        )
    assert case.store.profile() == newer


def test_new_session_never_resets_month_and_clock_regression_blocks_start(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    receipt = case.store.admit("first", case.prepared()).receipt
    complete(case, receipt)
    with case.database.transaction() as db:
        db.execute("UPDATE budget_scopes SET settled=50,reserved=30 WHERE kind='month'")
    second = case.store.create_session("second-session", "More research").receipt
    assert second.target_id is not None
    prepared = replace(
        case.prepared(), intent=replace(case.prepared().intent, session_id=second.target_id)
    )
    case.wall.value -= 1
    assert case.store.admit("regressed", prepared).receipt.reason == "clock_regressed"
    case.wall.value += 1
    accepted = case.store.admit("next", prepared).receipt
    assert accepted.disposition == "accepted"
    with case.database.transaction() as db:
        assert tuple(
            db.execute("SELECT settled,reserved FROM budget_scopes WHERE kind='month'").fetchone()
        ) == (50, 30)


def test_absent_session_and_preflight_rejection_create_no_run(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    invalid = replace(case.prepared(), intent=replace(case.prepared().intent, session_id="absent"))
    assert case.store.admit("unknown", invalid).receipt.reason == "unknown_session"
    rejected = case.store.reject("invalid", case.prepared().intent, "invalid_graph")
    assert case.store.admit("invalid", case.prepared()).receipt == rejected.receipt
    with case.database.transaction() as db:
        assert db.execute("SELECT count(*) FROM managed_runs").fetchone()[0] == 0
