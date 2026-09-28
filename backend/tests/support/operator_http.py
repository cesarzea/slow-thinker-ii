"""Authenticated HTTP tests use real coordinator ownership and SQLite command transactions."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import httpx
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import OperatorAccess, operator_router
from slow_thinker_ii.adapters.sqlite import SqliteOperatorQueries
from slow_thinker_ii.contracts import JsonObject, json_object

from .coordinator import CoordinatorCase, coordinator_case

TOKEN = "synthetic_operator_token_01234567890123456789"
ORIGIN = "http://127.0.0.1:8000"


@dataclass
class HttpCase:
    case: CoordinatorCase
    client: httpx.AsyncClient
    queries: SqliteOperatorQueries

    def start(self, command_id: str = "start") -> JsonObject:
        intent = self.case.base.prepared().intent
        return {
            "schema_version": "0.1-draft",
            "command_id": command_id,
            "session_id": intent.session_id,
            "graph_id": intent.graph_id,
            "graph_revision": intent.graph_revision,
            "configuration_revision": intent.configuration_revision,
            "input": {"p": "test"},
        }

    async def close(self) -> None:
        self.case.preparer.release.set()
        self.case.preparer.operation.release.set()
        assert not (await self.case.coordinator.close()).runs
        await self.client.aclose()


def http_case(directory: Path, limit: int = 1_048_576) -> HttpCase:
    case = coordinator_case(directory)
    access = OperatorAccess(TOKEN, (ORIGIN,), ("127.0.0.1:8000",))
    queries = SqliteOperatorQueries(case.base.database, b"k" * 32, 2, case.base.wall)
    app = FastAPI()
    app.include_router(operator_router(case.coordinator, case.commands, queries, access, limit))
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=ORIGIN,
        headers={"authorization": "Bearer " + TOKEN, "origin": ORIGIN},
    )
    return HttpCase(case, client, queries)


class JsonResponse(Protocol):
    def json(self) -> object: ...


def payload(response: JsonResponse) -> JsonObject:
    return json_object(response.json())
