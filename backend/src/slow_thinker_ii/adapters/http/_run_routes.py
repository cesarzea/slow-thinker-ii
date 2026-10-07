"""Operator routes for runs, their events and stops, and budget usage."""

from fastapi import Request, Response

from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._operator_input import (
    integer,
    invalid_request,
    json_body,
    known_fields,
    number_field,
    query,
    reply,
    text_field,
)
from ._settings import HttpServices

RUNS_PAGE = 100  # the use case clamps `limit` to 1–100
EVENTS_PAGE = 500  # and to 1–500 for events


def _source(body: JsonObject) -> tuple[int | None, int | None]:
    """Exactly one of `version` and `change`: what the run executes."""
    if ("version" in body) == ("change" in body):
        raise invalid_request("A run needs exactly one of “version” and “change”.")
    if "version" in body:
        return number_field(body, "version"), None
    return None, number_field(body, "change")


class RunRoutes:
    def __init__(self, services: HttpServices, limit: int) -> None:
        self._runs = services.runs
        self._usage = services.usage
        self._limit = limit

    async def start(self, request: Request) -> Response:
        """`input` absent or null runs the Trigger's configured message."""
        query(request)
        body = await json_body(request, self._limit)
        known_fields(body, ("graph_id",), ("version", "change", "input"))
        graph_id = text_field(body, "graph_id")
        version, change = _source(body)
        run_id = await self._runs.start(graph_id, version, body.get("input"), change=change)
        return reply({"run_id": run_id}, 202)

    async def runs(self, request: Request) -> Response:
        parameters = query(request, ("graph_id", "limit"))
        graph_id = parameters.get("graph_id") or None
        limit = integer(parameters, "limit", RUNS_PAGE)
        runs: list[JsonValue] = [record.to_json() for record in self._runs.runs(graph_id, limit)]
        return reply({"runs": runs})

    async def run(self, request: Request, run_id: str) -> Response:
        query(request)
        return reply(self._runs.run(run_id).to_json())

    async def events(self, request: Request, run_id: str) -> Response:
        parameters = query(request, ("after", "limit"))
        after = integer(parameters, "after", 0, signed=False)
        limit = integer(parameters, "limit", EVENTS_PAGE)
        return reply(self._runs.events(run_id, after, limit).to_json())

    async def stop(self, request: Request, run_id: str) -> Response:
        """`202` with the current status, or the final one when the run has finished."""
        query(request)
        known_fields(await json_body(request, self._limit), ())
        return reply({"status": self._runs.stop(run_id)}, 202)

    async def usage(self, request: Request) -> Response:
        query(request)
        return reply(self._usage.usage())
