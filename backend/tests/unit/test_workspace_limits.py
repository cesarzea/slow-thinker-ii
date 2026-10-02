"""Limit changes remain exact, bounded and tied to immutable configuration identities."""

from dataclasses import replace

import pytest
from slow_thinker_ii.application import ExecutionConfiguration, LimitsProfile, workspace
from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object


def profile() -> ExecutionConfiguration:
    return ExecutionConfiguration(
        "current",
        LimitsProfile("policy", 90, 20, 10, 5, 100, 8, 1048576, 1000000000, 2000000000, 3000000000),
        "{}",
    )


def command(changes: JsonObject) -> workspace.LimitsCommand:
    return workspace.limits_command(
        {"command_id": "a" * 32, "expected_revision": "current", "limits": changes}
    )


def test_exact_limits_roundtrip_and_original_preservation() -> None:
    original = profile()
    update = command({"call_seconds": 1.25, "run_budget": "0.123456789", "max_depth": 4})
    changed = workspace.apply_limits(original, update, original.limits)
    assert changed.revision == "settings-" + "a" * 32
    assert changed.limits.revision == original.limits.revision
    assert changed.limits.run_budget == 123456789
    assert changed.limits.call_seconds == 1.25 and changed.limits.max_depth == 4
    assert changed.resources_json == original.resources_json
    assert original.limits.call_seconds == 20
    assert (
        json_object(json_object(decode_json(update.to_json()))["limits"])["run_budget"]
        == "0.123456789"
    )
    assert workspace.limits_value(changed.limits)["run_budget"] == "0.123456789"
    assert workspace.within_limits(changed.limits, original.limits)
    assert not workspace.within_limits(original.limits, changed.limits)


@pytest.mark.parametrize(
    "changes",
    [
        {},
        {"unsupported": 1},
        {"call_seconds": 0},
        {"call_seconds": False},
        {"call_seconds": "1"},
        {"call_seconds": float("inf")},
        {"call_seconds": -1},
        {"call_seconds": 10**1000},
        {"max_calls": 1.0},
        {"max_calls": False},
        {"max_calls": 0},
        {"run_budget": 1},
        {"run_budget": "-1"},
        {"run_budget": "0.0000000001"},
        {"run_budget": "1" * 65},
    ],
)
def test_invalid_limits_command(changes: JsonObject) -> None:
    with pytest.raises(workspace.WorkspaceError, match="invalid_limits"):
        command(changes)


@pytest.mark.parametrize(
    "field, value",
    [
        ("command_id", "A" * 32),
        ("command_id", None),
        ("expected_revision", ""),
        ("expected_revision", "x" * 4097),
        ("expected_revision", 1),
        ("limits", []),
    ],
)
def test_invalid_command_identity_or_container(field: str, value: JsonValue) -> None:
    body: JsonObject = {
        "command_id": "a" * 32,
        "expected_revision": "current",
        "limits": {"max_calls": 1},
    }
    body[field] = value
    with pytest.raises(workspace.WorkspaceError, match="invalid_limits"):
        workspace.limits_command(body)


def test_unknown_command_fields_ceiling_and_cross_field_duration() -> None:
    with pytest.raises(workspace.WorkspaceError, match="invalid_limits"):
        workspace.limits_command(
            {
                "command_id": "a" * 32,
                "expected_revision": "current",
                "limits": {"max_calls": 1},
                "other": True,
            }
        )
    original = profile()
    for changes in ({"run_seconds": 91}, {"run_budget": "1.000000001"}):
        with pytest.raises(workspace.WorkspaceError, match="invalid_limits"):
            workspace.apply_limits(original, command(json_object(changes)), original.limits)
    with pytest.raises(workspace.WorkspaceError, match="invalid_limits"):
        workspace.apply_limits(original, command({"run_seconds": 10}), original.limits)
    assert (
        workspace.apply_limits(
            original, command({"run_budget": "0"}), original.limits
        ).limits.run_budget
        == 0
    )
    assert workspace.within_limits(original.limits, replace(original.limits, max_depth=9))
