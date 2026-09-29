"""Narrow typed boundary for the installed LangGraph distribution without a PEP 561 marker."""

from collections.abc import Awaitable, Callable
from importlib import import_module
from typing import Protocol, TypedDict, cast


class GraphState(TypedDict):
    content: str


class CompiledGraph(Protocol):
    async def ainvoke(self, input: GraphState) -> GraphState: ...


class Builder(Protocol):
    def add_node(
        self, node: str, action: Callable[[GraphState], Awaitable[GraphState]]
    ) -> object: ...
    def add_edge(self, source: str, target: str) -> object: ...
    def compile(self) -> CompiledGraph: ...


class GraphModule(Protocol):
    START: str
    END: str

    def StateGraph(self, _state_schema: type[GraphState], /) -> Builder: ...


def graph_module() -> GraphModule:
    return cast(GraphModule, import_module("langgraph.graph"))
