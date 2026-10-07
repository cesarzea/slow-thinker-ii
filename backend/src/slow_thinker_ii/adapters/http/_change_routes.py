"""Operator routes for a graph's branches, their append-only changes and activation."""

from fastapi import Request, Response

from slow_thinker_ii.application import rfc3339
from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._operator_input import (
    integer,
    json_body,
    known_fields,
    number_field,
    numbered,
    query,
    reply,
    start_field,
    text_field,
)
from ._settings import HttpServices

CHANGES_PAGE = 50  # the default page; the use case serves at most 100 changes


class ChangeRoutes:
    def __init__(self, services: HttpServices, limit: int) -> None:
        self._library = services.graphs
        self._limit = limit

    async def branches(self, request: Request, graph_id: str) -> Response:
        query(request)
        branches: list[JsonValue] = [item.to_json() for item in self._library.branches(graph_id)]
        return reply({"branches": branches})

    async def create_branch(self, request: Request, graph_id: str) -> Response:
        """A branch whose first change holds the document of one version or one change."""
        query(request)
        body = await json_body(request, self._limit)
        known_fields(body, ("name", "from"))
        name, (kind, number) = text_field(body, "name"), start_field(body)
        version, change = (number, None) if kind == "version" else (None, number)
        first = self._library.create_branch(
            graph_id, name, from_version=version, from_change=change
        )
        return reply({"name": name, "change": first}, 201)

    async def record(self, request: Request, graph_id: str) -> Response:
        """`201` for a new change; `200` with the branch's latest change when it is identical."""
        query(request)
        body = await json_body(request, self._limit)
        known_fields(body, ("branch", "document"))
        branch = text_field(body, "branch")
        change, at, created = self._library.record_change(graph_id, branch, body["document"])
        return reply({"change": change, "at": rfc3339(at)}, 201 if created else 200)

    async def changes(self, request: Request, graph_id: str) -> Response:
        """Newest first, of one branch or (without `branch`) of all; `before` is exclusive."""
        parameters = query(request, ("branch", "before", "limit"))
        branch = parameters.get("branch") or None
        before = integer(parameters, "before", 0, signed=False) if "before" in parameters else None
        limit = integer(parameters, "limit", CHANGES_PAGE)
        found = self._library.changes(graph_id, branch, before, limit)
        changes: list[JsonValue] = [change.to_json() for change in found]
        return reply({"changes": changes})

    async def change(self, request: Request, graph_id: str, change: str) -> Response:
        query(request)
        number = numbered(change, "change", graph_id)
        return reply(self._library.change(graph_id, number).to_json())

    async def activate(self, request: Request, graph_id: str) -> Response:
        """Activates a change as the next version on its branch: `201 {"version", "branch",
        "change"}`."""
        query(request)
        body = await json_body(request, self._limit)
        known_fields(body, ("change",))
        version = self._library.activate(graph_id, number_field(body, "change"))
        activated: JsonObject = {
            "version": version.version,
            "branch": version.branch,
            "change": version.change,
        }
        return reply(activated, 201)
