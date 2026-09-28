"""Permissions follow authenticated receivers and cannot be inferred from routing."""

import pytest
from slow_thinker_ii.access import AccessDenied
from support.authority import MEMORY, MODEL, PROPOSER, REVIEWER, Clock, alias, authority


def test_filtered_discovery_and_receiver_permissions() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    assert [item.address for item in service.discover(parent.token)] == [REVIEWER]
    child = service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    assert {item.address for item in service.discover(child.token)} == {MODEL, PROPOSER}
    model_alias = alias(service, child.token, MODEL)
    with pytest.raises(AccessDenied, match="operation_denied"):
        service.invoke(parent.token, model_alias)
    model = service.invoke(child.token, model_alias)
    assert model.context.caller == "reviewer"
    assert model.context.parent_call_id == child.context.call_id
    assert model.context.activation_id == parent.context.activation_id
    assert model.context.depth == 3
    assert model.context.run_id == "run" and model.context.graph_revision == "revision"
    assert service.discover(model.token) == ()


def test_unknown_alias_and_unscheduled_resource_are_denied() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    with pytest.raises(AccessDenied, match="operation_denied"):
        service.invoke(parent.token, "memory/read")
    with pytest.raises(AccessDenied, match="scheduler_operation_denied"):
        service.schedule(MEMORY)


def test_busy_ancestor_cannot_be_queued_behind_its_child() -> None:
    service = authority(Clock())
    parent = service.schedule(PROPOSER)
    child = service.invoke(parent.token, alias(service, parent.token, REVIEWER))
    with pytest.raises(AccessDenied, match="instance_busy"):
        service.invoke(child.token, alias(service, child.token, PROPOSER))
    with pytest.raises(AccessDenied, match="instance_busy"):
        service.schedule(REVIEWER)


def test_old_token_is_invalid_even_when_process_instance_is_reused() -> None:
    service = authority(Clock())
    first = service.schedule(PROPOSER)
    assert service.finish(first.context.call_id, succeeded=True).publish
    second = service.schedule(PROPOSER)
    assert first.token != second.token
    assert first.context.call_id != second.context.call_id
    assert first.context.attempt_id != second.context.attempt_id
    assert first.context.activation_id != second.context.activation_id
    with pytest.raises(AccessDenied, match="invalid_authority"):
        service.discover(first.token)
    assert service.discover(second.token)
    assert second.token not in repr(second)


def test_controller_calls_need_not_create_an_activation() -> None:
    service = authority(Clock())
    controller = service.schedule(PROPOSER, activation=False)
    child = service.invoke(controller.token, alias(service, controller.token, REVIEWER))
    assert controller.context.activation_id is None and child.context.activation_id is None


def test_grants_do_not_cross_runs_or_survive_registry_restart() -> None:
    first, second = authority(Clock()), authority(Clock())
    token = first.schedule(PROPOSER).token
    for untrusted in (token, "", "invented"):
        with pytest.raises(AccessDenied, match="invalid_authority"):
            second.discover(untrusted)
