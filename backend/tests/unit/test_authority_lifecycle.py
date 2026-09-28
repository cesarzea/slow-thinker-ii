"""Completion, revocation and bounded admission serialize without awaiting components."""

from concurrent.futures import ThreadPoolExecutor
from functools import partial

import pytest
from slow_thinker_ii.access import AccessDenied, CallAuthority, InvocationLease, OperationAddress
from support.authority import MODEL, PROPOSER, REVIEWER, Clock, alias, authority


def test_nested_deadlines_never_extend_parent_time() -> None:
    clock = Clock()
    service = authority(clock)
    parent = service.schedule(PROPOSER)
    clock.now = 29
    child = service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    assert child.context.deadline == parent.context.deadline == 30
    clock.now = 30
    with pytest.raises(AccessDenied, match="invalid_authority"):
        service.discover(child.token)
    ended = service.finish(child.context.call_id, succeeded=True)
    assert not ended.publish and ended.reason == "deadline_expired"


def test_run_deadline_blocks_admission_and_late_completion() -> None:
    clock = Clock()
    service = authority(clock)
    clock.now = 99
    parent = service.schedule(PROPOSER)
    assert parent.context.deadline == 100
    clock.now = 100
    with pytest.raises(AccessDenied, match="run_closed"):
        service.schedule(REVIEWER)
    assert service.finish(parent.context.call_id, succeeded=True).reason == "deadline_expired"


def test_parent_with_active_children_fails_and_revokes_entire_subtree() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    child = service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    grandchild = service.invoke(child.token, alias(service, child.token, MODEL))
    ended = service.finish(parent.context.call_id, succeeded=True)
    assert not ended.publish and ended.reason == "unfinished_children"
    assert ended.revoked == (
        parent.context.call_id,
        child.context.call_id,
        grandchild.context.call_id,
    )
    for item in (parent, child, grandchild):
        with pytest.raises(AccessDenied, match="invalid_authority"):
            service.discover(item.token)
    assert service.finish(child.context.call_id, succeeded=True).reason == "authority_closed"


def test_stop_is_idempotent_and_preserves_already_returned_completion() -> None:
    service = authority(Clock())
    completed = service.schedule(PROPOSER)
    outcome = service.finish(completed.context.call_id, succeeded=True)
    active = service.schedule(REVIEWER)
    assert service.stop() == (active.context.call_id,)
    assert service.stop() == (active.context.call_id,)
    assert outcome.publish
    assert not service.finish(active.context.call_id, succeeded=True).publish
    assert service.stop() == ()
    with pytest.raises(AccessDenied, match="run_closed"):
        service.discover(active.token)


def test_depth_and_total_call_count_include_nested_work() -> None:
    service = authority(Clock(), calls=2, depth=1)
    parent = service.schedule(PROPOSER)
    with pytest.raises(AccessDenied, match="depth_limit"):
        service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    assert service.finish(parent.context.call_id, succeeded=True).publish
    last = service.schedule(REVIEWER)
    assert service.finish(last.context.call_id, succeeded=True).publish
    with pytest.raises(AccessDenied, match="call_limit"):
        service.schedule(PROPOSER)


def attempt(service: CallAuthority, target: OperationAddress) -> InvocationLease | str:
    try:
        return service.schedule(target)
    except AccessDenied as error:
        return error.code


def test_concurrent_admissions_cannot_spend_the_same_call_slot() -> None:
    service = authority(Clock(), calls=1)
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(partial(attempt, service), (PROPOSER, REVIEWER)))
    assert sum(isinstance(result, InvocationLease) for result in results) == 1
    assert results.count("call_limit") == 1


def test_revoked_child_stays_busy_until_execution_has_actually_finished() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    child = service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    assert service.finish(parent.context.call_id, succeeded=True).reason == "unfinished_children"
    with pytest.raises(AccessDenied, match="instance_busy"):
        service.schedule(REVIEWER)
    assert not service.finish(child.context.call_id, succeeded=True).publish
    assert service.schedule(REVIEWER).context.target == REVIEWER


def test_failed_operation_revokes_authority_without_publishing_output() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    ended = service.finish(parent.context.call_id, succeeded=False)
    assert not ended.publish and ended.reason == "operation_failed"
    with pytest.raises(AccessDenied, match="invalid_authority"):
        service.discover(parent.token)


def test_stop_includes_revoked_children_still_requiring_cancellation() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    child = service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    service.finish(parent.context.call_id, succeeded=False)
    assert service.stop() == (child.context.call_id,)
    assert service.stop() == (child.context.call_id,)
    service.finish(child.context.call_id, succeeded=False)
    assert service.stop() == ()
