"""Serve the actual application with an explicitly selected installed bundle and local provider."""

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import httpx
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.preparation import ServiceEndpoints
from slow_thinker_ii.bootstrap import ExecutionSetup, create_app
from support.catalog import RecordedCatalog
from support.native_server import serve
from support.operator_http import TOKEN

from .conftest import PreparedBundle
from .coordinator_fixture import InstalledPreparer
from .graph_helpers import compile_graph


@asynccontextmanager
async def operator_application(
    directory: Path, bundle: PreparedBundle, name: str, provider: int
) -> AsyncGenerator[tuple[httpx.AsyncClient, int]]:
    installed = await asyncio.to_thread(compile_graph, bundle, name)
    prepared = InstalledPreparer(bundle, installed, directory)
    outer = FastAPI()
    async with serve(outer) as port:
        origin = f"http://127.0.0.1:{port}"
        setup = execution_setup(prepared, port, provider)
        app = create_app(directory / "application.sqlite", RecordedCatalog(), setup)
        outer.mount("/", app)
        async with (
            app.router.lifespan_context(app),
            httpx.AsyncClient(
                base_url=origin,
                timeout=60,
                headers={"authorization": "Bearer " + TOKEN, "origin": origin},
            ) as client,
        ):
            yield client, len(installed.plan.nodes)


def execution_setup(prepared: InstalledPreparer, port: int, provider: int) -> ExecutionSetup:
    origin = f"http://127.0.0.1:{port}"
    return ExecutionSetup(
        prepared.configuration,
        prepared.bundle.catalog,
        tuple(item.descriptor_json for item in prepared.selected),
        ServiceEndpoints(origin + "/v1", f"http://127.0.0.1:{provider}/v1"),
        prepared.secrets,
        OperatorAccess(TOKEN, (origin,), (f"127.0.0.1:{port}",)),
        b"k" * 32,
        prepared.directory / "hosts",
        45,
        4,
    )
