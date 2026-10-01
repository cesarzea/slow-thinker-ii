"""Expose catalogue data through a typed operator HTTP boundary."""

from fastapi import APIRouter, Request, Response
from pydantic import BaseModel

from slow_thinker_ii.application import ExperimentCatalog
from slow_thinker_ii.contracts import JsonObject, decode_json, json_object
from slow_thinker_ii.definitions import GraphSummary

from ._operator_errors import operator_error
from ._operator_replies import representation


class NodeReply(BaseModel):
    id: str
    component: str


class GraphReply(BaseModel):
    graph_id: str
    revision: str
    participants: int
    nodes: list[NodeReply]
    input_schema: JsonObject


def _reply(graph: GraphSummary) -> GraphReply:
    nodes = [NodeReply(id=node.node_id, component=node.component_id) for node in graph.nodes]
    return GraphReply(
        graph_id=graph.graph_id,
        revision=graph.revision,
        participants=graph.participant_count,
        nodes=nodes,
        input_schema=json_object(decode_json(graph.input_schema_json)),
    )


def catalog_router(catalog: ExperimentCatalog) -> APIRouter:
    router = APIRouter()

    def list_graphs() -> list[GraphReply]:
        return [_reply(graph) for graph in catalog.list_graphs()]

    async def detail(request: Request, graph_id: str, revision: str) -> Response:
        try:
            return representation(request, catalog.graph(graph_id, revision), 1_048_576)
        except Exception as error:
            return operator_error(error)

    router.add_api_route("/api/v1/graphs", list_graphs, methods=["GET"])
    router.add_api_route("/api/v1/graphs/{graph_id}/revisions/{revision}", detail, methods=["GET"])
    return router
