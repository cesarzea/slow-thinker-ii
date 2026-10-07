"""Invocation grants identify one call, expire exactly, and are stored only as digests."""

import hashlib
import math
from concurrent.futures import ThreadPoolExecutor

import pytest
from slow_thinker_ii.access import Caller, Grants


class Clock:
    def __init__(self) -> None:
        self.now = 100.0

    def __call__(self) -> float:
        return self.now


def caller(run_id: str = "run-1", activation_id: str = "a1") -> Caller:
    return Caller(run_id=run_id, node_id="proposer", position="node", activation_id=activation_id)


def test_issue_and_resolve() -> None:
    grants = Grants(Clock())
    token = grants.issue(caller(), 5)
    resolved = grants.resolve(token)
    assert resolved == caller()
    assert resolved is not None
    assert (resolved.run_id, resolved.node_id) == ("run-1", "proposer")
    assert (resolved.position, resolved.activation_id) == ("node", "a1")
    assert len(token) == 43
    assert grants.issue(caller(), 5) != token


def test_unknown_tokens_resolve_to_nothing() -> None:
    grants = Grants(Clock())
    grants.issue(caller(), 5)
    assert grants.resolve("not-a-grant") is None
    assert grants.resolve("") is None


def test_revocation_is_idempotent() -> None:
    grants = Grants(Clock())
    token = grants.issue(caller(), 5)
    other = grants.issue(caller(activation_id="a2"), 5)
    grants.revoke(token)
    grants.revoke(token)
    grants.revoke("unknown")
    assert grants.resolve(token) is None
    assert grants.resolve(other) == caller(activation_id="a2")


def test_run_wide_revocation() -> None:
    grants = Grants(Clock())
    first = grants.issue(caller(), 5)
    second = grants.issue(Caller("run-1", "reviewer", "output", "a3"), 5)
    kept = grants.issue(caller(run_id="run-2"), 5)
    assert (grants.active("run-1"), grants.active("run-2")) == (2, 1)
    grants.revoke_run("run-1")
    grants.revoke_run("run-3")
    assert (grants.resolve(first), grants.resolve(second)) == (None, None)
    assert grants.resolve(kept) == caller(run_id="run-2")
    assert (grants.active("run-1"), grants.active("run-2")) == (0, 1)


def test_expiry_at_the_exact_boundary() -> None:
    clock = Clock()
    grants = Grants(clock)
    token = grants.issue(caller(), 5)
    clock.now = 104.5
    assert grants.resolve(token) == caller()
    assert grants.active("run-1") == 1
    clock.now = 105.0
    assert grants.active("run-1") == 0
    assert grants.resolve(token) is None
    clock.now = 90.0
    assert grants.resolve(token) is None


def test_expired_grants_are_removed_lazily() -> None:
    clock = Clock()
    grants = Grants(clock)
    grants.issue(caller(), 1)
    longer = grants.issue(caller(activation_id="a2"), 10)
    stored = vars(grants)["_grants"]
    clock.now = 102.0
    assert len(stored) == 2
    assert grants.active("run-1") == 1
    assert len(stored) == 2
    grants.issue(caller(activation_id="a3"), 1)
    assert len(stored) == 2
    clock.now = 104.0
    assert grants.resolve(longer) == caller(activation_id="a2")
    assert len(stored) == 1


@pytest.mark.parametrize("ttl", [0.0, -1.0, math.nan])
def test_time_to_live_must_be_positive(ttl: float) -> None:
    with pytest.raises(ValueError, match="^A grant requires a positive time to live$"):
        Grants(Clock()).issue(caller(), ttl)


def test_only_digests_are_stored() -> None:
    grants = Grants(Clock())
    token = grants.issue(caller(), 5)
    state = repr(vars(grants))
    assert token not in state
    assert repr(hashlib.sha256(token.encode()).digest()) in state
    assert token not in repr(grants)


def test_concurrent_issue_and_revoke() -> None:
    grants = Grants(Clock())
    kept = [grants.issue(caller(activation_id=f"k{index}"), 60) for index in range(50)]

    def churn(index: int) -> None:
        token = grants.issue(caller(activation_id=f"c{index}"), 60)
        grants.revoke(token)

    def issue_for_another_run(index: int) -> str:
        return grants.issue(caller(run_id="run-2", activation_id=f"r{index}"), 60)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(churn, range(400)))
        issued = list(pool.map(issue_for_another_run, range(100)))
    assert grants.active("run-1") == 50
    assert grants.active("run-2") == 100
    assert all(grants.resolve(token) is not None for token in kept + issued)
    assert len(set(issued)) == 100
