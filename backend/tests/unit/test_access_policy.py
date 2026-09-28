"""Malformed policy and limits fail before any business authority can be issued."""

import pytest
from slow_thinker_ii.access import (
    AccessPolicy,
    CallAuthority,
    CallLimits,
    OperationAddress,
    Permission,
)
from support.authority import MODEL, PROPOSER, REVIEWER, Clock


@pytest.mark.parametrize("instance,operation", [("", "generate"), ("agent", "")])
def test_operation_identity_is_required(instance: str, operation: str) -> None:
    with pytest.raises(ValueError, match="identities"):
        OperationAddress(instance, operation)


@pytest.mark.parametrize("operations", [(), (PROPOSER, PROPOSER)])
def test_empty_or_duplicate_declarations(operations: tuple[OperationAddress, ...]) -> None:
    with pytest.raises(ValueError, match="unique operations"):
        AccessPolicy(operations, (), ())


@pytest.mark.parametrize(
    "permission", [Permission("unknown", MODEL), Permission("proposer", MODEL)]
)
def test_permissions_require_declared_caller_and_target(permission: Permission) -> None:
    with pytest.raises(ValueError, match="Permissions"):
        AccessPolicy((PROPOSER,), (permission,), (PROPOSER,))


def test_scheduler_cannot_reference_an_undeclared_operation() -> None:
    with pytest.raises(ValueError, match="Scheduled"):
        AccessPolicy((PROPOSER,), (), (MODEL,))


@pytest.mark.parametrize("count", [0, -1, True])
def test_call_and_depth_limits_require_positive_integers(count: int) -> None:
    with pytest.raises(ValueError, match="positive integers"):
        CallLimits(count, 2, 10)
    with pytest.raises(ValueError, match="positive integers"):
        CallLimits(2, count, 10)


@pytest.mark.parametrize("seconds", [0, -1, True, float("nan"), float("inf")])
def test_duration_is_finite_and_positive(seconds: float) -> None:
    with pytest.raises(ValueError, match="duration"):
        CallLimits(2, 2, seconds)


@pytest.mark.parametrize(
    "run,revision,deadline",
    [
        ("", "revision", 100),
        ("run", "", 100),
        ("run", "revision", 10),
        ("run", "revision", float("nan")),
        ("run", "revision", float("inf")),
    ],
)
def test_run_identity_and_deadline_are_required(run: str, revision: str, deadline: float) -> None:
    policy = AccessPolicy((PROPOSER,), (), (PROPOSER,))
    with pytest.raises(ValueError, match="Run identity"):
        CallAuthority(run, revision, policy, CallLimits(2, 2, 10), deadline, Clock())


def test_aliases_are_opaque_and_deterministic_for_a_frozen_operation_set() -> None:
    permissions = (Permission("proposer", REVIEWER),)
    first = AccessPolicy((PROPOSER, REVIEWER), permissions, (PROPOSER,))
    second = AccessPolicy((REVIEWER, PROPOSER), permissions, (PROPOSER,))
    published = first.discover("proposer")
    assert published == second.discover("proposer")
    assert published[0].alias.startswith("op_")
    assert "reviewer" not in published[0].alias
    assert first.resolve("proposer", published[0].alias) == REVIEWER
