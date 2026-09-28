"""Actual HTTP commands retain durable receipts and single execution ownership."""

import asyncio

from slow_thinker_ii.application import PreparationRejected
from support.coordinator import eventually
from support.operator_http import HttpCase, payload


async def test_create_session_and_replay(api: HttpCase) -> None:
    body = {"schema_version": "0.1-draft", "command_id": "session-http", "name": "Research"}
    created = await api.client.post("/api/v1/sessions", json=body)
    assert created.status_code == 202
    repeated = payload(await api.client.post("/api/v1/sessions", json=body))
    assert repeated["replayed"] is True and repeated["target_id"] == payload(created)["target_id"]
    body["name"] = "Conflicting intent"
    assert (await api.client.post("/api/v1/sessions", json=body)).status_code == 409


async def test_duplicate_start_runs_once_and_is_observable(api: HttpCase) -> None:
    first, second = await asyncio.gather(
        *(api.client.post("/api/v1/runs", json=api.start()) for _ in range(2))
    )
    assert first.status_code == second.status_code == 202
    identity = str(payload(first)["target_id"])
    assert payload(second)["target_id"] == identity
    await eventually(lambda: not api.case.coordinator.pending().runs)
    status = payload(await api.client.get(f"/api/v1/runs/{identity}"))
    assert status["state"] == "completed" and status["cleanup"] == "confirmed"
    assert status["calls"] == {"completed": 1}
    assert len(api.case.preparer.operation.calls) == 1
    command = payload(await api.client.get("/api/v1/commands/start"))
    assert command["target_id"] == identity
    assert not (await api.client.get(f"/api/v1/runs/{identity}/definition")).is_error


async def test_stop_and_repeated_stop_retain_receipts(api: HttpCase) -> None:
    api.case.preparer.operation.release.clear()
    started = payload(await api.client.post("/api/v1/runs", json=api.start()))
    await asyncio.wait_for(api.case.preparer.operation.started.wait(), 5)
    url = f"/api/v1/runs/{started['target_id']}/stop"
    body = {"schema_version": "0.1-draft", "command_id": "stop"}
    assert (await api.client.post(url, json=body)).status_code == 202
    await eventually(lambda: not api.case.coordinator.pending().runs)
    assert payload(await api.client.post(url, json=body))["replayed"] is True
    body["command_id"] = "stop-later"
    assert payload(await api.client.post(url, json=body))["disposition"] == "already_terminal"
    run = payload(await api.client.get(f"/api/v1/runs/{started['target_id']}"))
    assert run["state"] == "cancelled"


async def test_withdrawn_intent_cannot_start_later(api: HttpCase) -> None:
    body = {"schema_version": "0.1-draft", "command_id": "start"}
    withdrawn = await api.client.post("/api/v1/commands/start/withdraw", json=body)
    assert payload(withdrawn)["disposition"] == "withdrawn"
    late = payload(await api.client.post("/api/v1/runs", json=api.start()))
    assert late["disposition"] == "withdrawn" and late["replayed"] is True
    assert not api.case.preparer.calls


async def test_rejected_start_is_durable(api: HttpCase) -> None:
    api.case.preparer.failure = PreparationRejected("invalid_graph_or_resource_configuration")
    rejected = payload(await api.client.post("/api/v1/runs", json=api.start()))
    assert rejected["disposition"] == "rejected"
    api.case.preparer.failure = None
    replayed = payload(await api.client.post("/api/v1/runs", json=api.start()))
    assert replayed["replayed"] is True and replayed["disposition"] == "rejected"
    assert not api.case.preparer.operation.calls


async def test_cancelling_http_waiter_does_not_abandon_start(api: HttpCase) -> None:
    api.case.preparer.release.clear()
    waiter = asyncio.create_task(api.client.post("/api/v1/runs", json=api.start()))
    await asyncio.wait_for(api.case.preparer.entered.wait(), 5)
    waiter.cancel()
    import pytest

    with pytest.raises(asyncio.CancelledError):
        await waiter
    api.case.preparer.release.set()
    await eventually(lambda: api.case.commands.command("start") is not None)
    assert payload(await api.client.get("/api/v1/commands/start"))["disposition"] == "accepted"
