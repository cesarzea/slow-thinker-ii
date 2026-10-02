"""Settings replay and activation are atomic without resetting financial commitments."""

from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from pathlib import Path

import pytest
from slow_thinker_ii.adapters.sqlite import SqliteConfigurationCommands, SqliteDatabase
from slow_thinker_ii.application import workspace
from slow_thinker_ii.contracts import JsonObject
from support.operator_commands import operator_case


def command(
    changes: JsonObject, revision: str = "configuration-1", identity: str = "a" * 32
) -> workspace.LimitsCommand:
    return workspace.limits_command(
        {"command_id": identity, "expected_revision": revision, "limits": changes}
    )


def test_concurrent_exact_replay_and_conflicting_body(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    commands = SqliteConfigurationCommands(case.database, case.wall)
    change = command({"call_seconds": 10})

    def apply(_: int) -> workspace.ConfigurationResult:
        return commands.change(change, case.profile.limits)

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(apply, range(2)))
    assert sorted(result.replayed for result in results) == [False, True]
    assert len({result.configuration_revision for result in results}) == 1
    with pytest.raises(workspace.WorkspaceError, match="configuration_conflict"):
        commands.change(command({"call_seconds": 9}), case.profile.limits)
    with pytest.raises(workspace.WorkspaceError, match="configuration_conflict"):
        commands.change(command({"call_seconds": 9}, identity="b" * 32), case.profile.limits)
    current = case.store.profile()
    assert current is not None and current.limits.call_seconds == 10


def test_active_execution_blocks_changes_but_receipt_replay_is_safe(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    commands = SqliteConfigurationCommands(case.database, case.wall)
    result = commands.change(command({"call_seconds": 10}), case.profile.limits)
    current = case.store.profile()
    assert current is not None
    prepared = case.prepared()
    prepared = replace(
        prepared,
        configuration=current,
        intent=replace(prepared.intent, configuration_revision=current.revision),
    )
    assert case.store.admit("active", prepared).receipt.disposition == "accepted"
    assert commands.change(command({"call_seconds": 10}), case.profile.limits).replayed
    with pytest.raises(workspace.WorkspaceError, match="configuration_active"):
        commands.change(
            command({"call_seconds": 9}, result.configuration_revision, "b" * 32),
            case.profile.limits,
        )


@pytest.mark.parametrize(
    "kind, identity, field",
    [
        ("session", "prior", "session_budget"),
        ("month", "2026-09", "month_budget"),
    ],
)
def test_commitment_denial_rolls_back_profile_and_receipt(
    tmp_path: Path, kind: str, identity: str, field: str
) -> None:
    case = operator_case(tmp_path)
    with case.database.transaction() as db:
        db.execute("INSERT INTO budget_scopes VALUES(?,?,10000,3000,1000)", (kind, identity))
    commands = SqliteConfigurationCommands(case.database, case.wall)
    with pytest.raises(workspace.WorkspaceError, match="budget_below_commitments"):
        commands.change(command({field: "0.000003999"}), case.profile.limits)
    assert case.store.profile() == case.profile
    with case.database.transaction() as db:
        assert db.execute("SELECT COUNT(*) FROM configuration_commands").fetchone()[0] == 0
        assert db.execute(
            "SELECT settled,reserved FROM budget_scopes WHERE kind=? AND scope_id=?",
            (kind, identity),
        ).fetchone()[:] == (3000, 1000)


def test_restart_preserves_user_settings_and_rejects_lower_startup_ceilings(tmp_path: Path) -> None:
    case = operator_case(tmp_path)
    commands = SqliteConfigurationCommands(case.database, case.wall)
    commands.change(command({"call_seconds": 10}), case.profile.limits)
    saved = case.store.profile()
    commands.initialize(case.profile)
    assert case.store.profile() == saved
    with pytest.raises(ValueError, match="exceed"):
        commands.initialize(
            replace(case.profile, limits=replace(case.profile.limits, call_seconds=9))
        )
    assert case.store.profile() == saved
    explicit = replace(case.profile, revision="different-resources", resources_json='{"new":true}')
    commands.initialize(explicit)
    assert case.store.profile() == explicit


def test_empty_database_rejects_changes_until_initial_configuration(tmp_path: Path) -> None:
    database = SqliteDatabase(tmp_path / "empty.sqlite")
    database.initialize()
    case = operator_case(tmp_path / "other")
    commands = SqliteConfigurationCommands(database, case.wall)
    with pytest.raises(workspace.WorkspaceError, match="operator_service_unavailable"):
        commands.change(command({"max_calls": 1}), case.profile.limits)
    commands.initialize(case.profile)
    assert commands.change(command({"max_calls": 1}), case.profile.limits).replayed is False
