"""The run owns ready operations while an independently supplied program advances the graph."""

from collections.abc import Mapping
from contextlib import AbstractAsyncContextManager
from typing import Protocol

from slow_thinker_ii.access import OperationAddress

from ._call_runner import ManagedCalls
from ._dispatch_ports import OperationPort


class RunEnvironment(Protocol):
    def open(
        self, deadline: float
    ) -> AbstractAsyncContextManager[Mapping[OperationAddress, OperationPort]]: ...
    def report(self) -> str: ...


class RunProgram(Protocol):
    async def execute(self, calls: ManagedCalls) -> str: ...
