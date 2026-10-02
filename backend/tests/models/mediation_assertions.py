"""Managed evidence retains caller, model selection, charge and deadline identity."""

from support.run_admission import outstanding

from .mediation_fixture import ModelCase


def assert_managed(case: ModelCase, settled: int, children: int) -> None:
    assert outstanding(case.run) == (0, 0, 0)
    with case.run.store.begin() as transaction:
        assert all(scope.settled == settled for scope in transaction.scopes(case.run.keys))
        records = [
            transaction.call(event.call_id)
            for event in transaction.events("run")
            if event.event == "call.requested"
            and event.call_id
            not in {case.parent.context.call_id, case.deepseek_parent.context.call_id}
            and event.call_id
        ]
    assert len(records) == children
    assert all(
        item.prepared.context.parent_call_id
        == (
            case.parent.context.call_id
            if item.prepared.context.target.instance == "openai-model"
            else case.deepseek_parent.context.call_id
        )
        for item in records
    )
    assert all(item.prepared.context.node_id == "two-provider-node" for item in records)
    assert all(item.prepared.charge is not None for item in records)


def assert_provider_selection(case: ModelCase) -> None:
    assert len(case.openai.native_requests) == len(case.deepseek.native_requests) == 1
    native = case.deepseek.native_requests[0]
    assert native["thinking"] == {"type": "enabled"} and native["reasoning_effort"] == "high"
    assert native["messages"] == [{"role": "user", "content": "second"}]
    assert all(
        invocation.deadline is not None
        and invocation.deadline <= case.deepseek_parent.context.deadline
        for invocation in case.deepseek.invocations
    )
    assert case.parent.token not in str(native)
    assert case.deepseek_parent.token not in str(native)
