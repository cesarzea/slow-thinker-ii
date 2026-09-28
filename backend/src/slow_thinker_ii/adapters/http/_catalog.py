"""Expose catalogue data through a typed operator HTTP boundary."""

from fastapi import APIRouter
from pydantic import BaseModel

from slow_thinker_ii.application import ExperimentCatalog
from slow_thinker_ii.definitions import GraphSummary


class NodeReply(BaseModel):
    id: str
    component: str


class GraphReply(BaseModel):
    graph_id: str
    revision: str
    participants: int
    nodes: list[NodeReply]


def _reply(graph: GraphSummary) -> GraphReply:
    nodes = [NodeReply(id=node.node_id, component=node.component_id) for node in graph.nodes]
    return GraphReply(
        graph_id=graph.graph_id,
        revision=graph.revision,
        participants=graph.participant_count,
        nodes=nodes,
    )


def catalog_router(catalog: ExperimentCatalog) -> APIRouter:
    router = APIRouter()

    def list_graphs() -> list[GraphReply]:
        return [_reply(graph) for graph in catalog.list_graphs()]

    router.add_api_route("/api/v1/graphs", list_graphs, methods=["GET"])
    return router
