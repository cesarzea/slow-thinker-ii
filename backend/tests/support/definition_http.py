"""Authenticated definition HTTP cases use the shared production SQLite library."""

from dataclasses import dataclass
from pathlib import Path

import httpx
from fastapi import FastAPI
from slow_thinker_ii.adapters.http import OperatorAccess, OperatorBoundary, definition_router
from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, encode_json, json_object

from .operator_http import ORIGIN, TOKEN
from .personal_library import personal_library
from .sequence_plans import graph_value

ROOT = "/api/v1/definitions"
PARENT = {"graph_id": "single-agent", "revision": "example-2"}


@dataclass(frozen=True)
class DefinitionHttp:
    service: library.ExperimentLibrary
    client: httpx.AsyncClient


def definition_http(directory: Path, limit: int = 1_048_576) -> DefinitionHttp:
    database = SqliteDatabase(directory / "definitions.sqlite")
    database.initialize()
    service = personal_library(database)
    app = FastAPI()
    access = OperatorAccess(TOKEN, (ORIGIN,), ("127.0.0.1:8000",))
    app.add_middleware(OperatorBoundary, access=access)
    app.include_router(definition_router(service, limit))
    client = httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url=ORIGIN,
        headers={"authorization": "Bearer " + TOKEN, "origin": ORIGIN},
    )
    return DefinitionHttp(service, client)


def variant(revision: str = "personal α / one") -> str:
    value = graph_value("single-agent")
    value["revision"], value["derived_from"] = revision, json_object(PARENT)
    value["extensions"] = {"fixture:float": 1.0, "fixture:integer": 9007199254740993}
    return encode_json(value)


def reference(revision: str = "personal α / one") -> dict[str, str]:
    return {"graph_id": "single-agent", "revision": revision}


def error_data(response: httpx.Response, status: int, code: str) -> JsonObject:
    assert response.status_code == status
    assert response.headers["cache-control"] == "no-store"
    assert len(response.content) <= 4096
    value = json_object(response.json())
    assert value["schema_version"] == "0.1-draft"
    error = json_object(value["error"])
    assert error["code"] == code and error["message"] == code.replace("_", " ")
    assert isinstance(error["request_id"], str) and error["request_id"]
    return error
