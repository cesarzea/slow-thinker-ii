"""Keep all ready MCP contexts in their owning task until graph work and cleanup finish."""

import asyncio
import json
from collections.abc import AsyncIterator, Mapping, Sequence
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.application import OperationPort, PricingPolicy

from ._connection import ComponentProcess
from ._operation import ProcessOperation


@dataclass(frozen=True)
class ProcessHost:
    instance: str
    process: ComponentProcess
    operations: tuple[tuple[str, PricingPolicy | None], ...]

    def __post_init__(self) -> None:
        names = [name for name, _ in self.operations]
        if not self.instance or not names or any(not name for name in names):
            raise ValueError("A host requires an instance and named operations")
        if len(set(names)) != len(names):
            raise ValueError("Host operation names must be unique")


class ProcessFleet:
    def __init__(self, hosts: Sequence[ProcessHost]) -> None:
        if len({host.instance for host in hosts}) != len(hosts):
            raise ValueError("Host instance identities must be unique")
        self._hosts = tuple(hosts)

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        operations: dict[OperationAddress, OperationPort] = {}
        async with AsyncExitStack() as stack:
            for host in self._hosts:
                async with asyncio.timeout_at(deadline):
                    connection = await stack.enter_async_context(host.process.connect())
                if set(connection.operation_names()) != {name for name, _ in host.operations}:
                    raise ValueError("Host bindings differ from ready operation contracts")
                for name, pricing in host.operations:
                    operations[OperationAddress(host.instance, name)] = ProcessOperation(
                        connection, name, pricing
                    )
            yield operations

    def report(self) -> str:
        return json.dumps([self._host_report(host) for host in self._hosts])

    @staticmethod
    def _host_report(host: ProcessHost) -> dict[str, str | int | bool | None]:
        outcome = host.process.outcome()
        if outcome is None:
            return {"instance": host.instance, "status": "not_started"}
        return {
            "instance": host.instance,
            "status": "stopped" if outcome.returncode is not None else "cleanup_failed",
            "pid": outcome.pid,
            "returncode": outcome.returncode,
            "forced": outcome.forced,
        }
