"""Operator routes for the catalog and the graph library: graphs and their versions."""

from fastapi import Request, Response

from slow_thinker_ii.catalog import OUTPUT, TRIGGER, ComponentDeclaration
from slow_thinker_ii.contracts import JsonValue

from ._operator_input import document_field, numbered, query, reply
from ._settings import HttpServices

PLATFORM_COMPONENTS = frozenset({TRIGGER, OUTPUT})


class GraphRoutes:
    def __init__(self, services: HttpServices, limit: int) -> None:
        self._catalog = services.catalog
        self._library = services.graphs
        self._limit = limit

    async def catalog(self, request: Request) -> Response:
        query(request)
        catalog = self._catalog()
        components: list[JsonValue] = [_component(item) for item in catalog.components()]
        llms: list[JsonValue] = [entry.document() for entry in catalog.llms()]
        return reply({"components": components, "llms": llms})

    async def validate(self, request: Request) -> Response:
        document = await document_field(request, self._limit)
        diagnostics: list[JsonValue] = [
            item.document() for item in self._library.validate(document)
        ]
        return reply({"diagnostics": diagnostics})

    async def graphs(self, request: Request) -> Response:
        query(request)
        graphs: list[JsonValue] = [summary.to_json() for summary in self._library.graphs()]
        return reply({"graphs": graphs})

    async def create(self, request: Request) -> Response:
        """A new graph from a draft document, as the first change of its `main` branch."""
        document = await document_field(request, self._limit)
        graph_id, branch, change = self._library.create(document)
        return reply({"id": graph_id, "branch": branch, "change": change}, 201)

    async def graph(self, request: Request, graph_id: str) -> Response:
        query(request)
        return reply(self._library.graph(graph_id).to_json())

    async def version(self, request: Request, graph_id: str, version: str) -> Response:
        query(request)
        number = numbered(version, "version", graph_id)
        return reply(self._library.version(graph_id, number).to_json())


def _component(declaration: ComponentDeclaration) -> JsonValue:
    """The declaration as validated, with its origin; the catalog's document is not changed."""
    origin = "platform" if declaration.ref in PLATFORM_COMPONENTS else "package"
    return {**declaration.document, "origin": origin}
