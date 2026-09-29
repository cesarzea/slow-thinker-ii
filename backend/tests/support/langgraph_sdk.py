"""Narrow typed boundary for the installed LangGraph distribution without a PEP 561 marker."""

from abc import abstractmethod
from collections.abc import Awaitable, Callable
from importlib import import_module
from typing import Protocol, TypedDict, cast


class GraphState(TypedDict):
    content: str


class CompiledGraph(Protocol):
    @abstractmethod
    async def ainvoke(self, input: GraphState) -> GraphState:
        raise NotImplementedError


class Builder(Protocol):
    @abstractmethod
    def add_node(self, node: str, action: Callable[[GraphState], Awaitable[GraphState]]) -> object:
        raise NotImplementedError

    @abstractmethod
    def add_edge(self, source: str, target: str) -> object:
        raise NotImplementedError

    @abstractmethod
    def compile(self) -> CompiledGraph:
        raise NotImplementedError


class GraphModule(Protocol):
    START: str
    END: str

    @abstractmethod
    def StateGraph(self, _state_schema: type[GraphState], /) -> Builder:
        raise NotImplementedError


def graph_module() -> GraphModule:
    return cast(GraphModule, import_module("langgraph.graph"))
