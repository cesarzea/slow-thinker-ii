"""Actual installed compositions repeat reviews through the authenticated MCP gateway."""

import asyncio
from pathlib import Path

import pytest
from fastapi import Request, Response
from slow_thinker_ii.adapters.http import mcp_router
from slow_thinker_ii.contracts import decode_json, encode_json, json_object
from support.native_server import gateway_app, serve
from support.upstream import Upstream

from .check_coordinator import finished
from .conftest import PreparedBundle
from .coordinator_fixture import InstalledPreparer, coordinator_setup
from .graph_helpers import compile_graph


class ReviewProvider(Upstream):
    def __init__(self, *, exhaust: bool) -> None:
        super().__init__()
        self.exhaust = exhaust

    async def complete(self, request: Request) -> Response:
        number = len(self.requests) + 1
        accepted = not self.exhaust and number >= 4
        self.content = (
            encode_json(
                {"accepted": accepted, "findings": [] if accepted else ["Add a concrete schedule"]}
            )
            if number % 2 == 0
            else f"Workshop proposal {number}"
        )
        return await super().complete(request)


@pytest.mark.parametrize("exhaust", [False, True])
async def test_installed_bounded_feedback(
    tmp_path: Path, prepared_bundle: PreparedBundle, *, exhaust: bool
) -> None:
    installed = await asyncio.to_thread(compile_graph, prepared_bundle, "bounded-review")
    preparer = InstalledPreparer(prepared_bundle, installed, tmp_path)
    coordinator, _, runs, intent = coordinator_setup(tmp_path, preparer)
    upstream = ReviewProvider(exhaust=exhaust)
    app = gateway_app(coordinator.gateway)
    app.include_router(mcp_router(coordinator.components))
    async with serve(upstream.app) as provider, serve(app) as gateway:
        preparer.gateway_port, preparer.provider_port = gateway, provider
        receipt = (await coordinator.start("start", intent)).receipt
        assert receipt.disposition == "accepted" and receipt.target_id is not None
        await finished(coordinator)
        with runs.begin() as transaction:
            run = transaction.run(receipt.target_id)
            assert run.state == ("failed" if exhaust else "completed")
            assert run.reason == ("activation_limit_reached" if exhaust else None)
            events = transaction.events(run.run_id)
        routes = [
            json_object(decode_json(event.payload_json))
            for event in events
            if event.event == "activation.routed"
        ]
        assert len(routes) == (6 if exhaust else 4)
        assert routes[1]["selected_port"] == "revise"
        assert len({str(item["activation_id"]) for item in routes}) == len(routes)
        assert len(upstream.requests) == len(routes)
        assert not (await coordinator.close()).runs
    assert not coordinator.failures()
