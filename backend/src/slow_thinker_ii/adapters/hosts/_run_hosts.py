"""The hosts of one run: calls routed by node and position, and their shutdown."""

import asyncio
import shutil
from collections.abc import Mapping
from contextlib import suppress
from pathlib import Path

from slow_thinker_ii.application import RunHosts
from slow_thinker_ii.contracts import JsonValue
from slow_thinker_ii.engine import CallContext, CallFailure, Emission, Position

from ._host import Host
from ._results import activation, recalled, remembered, selection

type HostKey = tuple[str, Position]


class LocalRunHosts(RunHosts):
    """Every package host of a run, keyed by node id and position."""

    def __init__(self, hosts: Mapping[HostKey, Host], directory: Path) -> None:
        self._hosts = dict(hosts)
        self._directory = directory

    async def activate(
        self, context: CallContext, message: JsonValue
    ) -> tuple[Emission, ...] | CallFailure:
        host = self._hosts.get((context.node_id, "node"))
        if host is None:
            return _missing(context.node_id)
        reply = await host.call("activate", {"message": message}, context)
        return reply if isinstance(reply, CallFailure) else activation(reply)

    async def select_output(
        self, context: CallContext, received: JsonValue, node_input: JsonValue
    ) -> Emission | CallFailure:
        host = self._hosts.get((context.node_id, "output"))
        if host is None:
            return _missing(context.node_id)
        arguments: dict[str, JsonValue] = {"received": received, "node_input": node_input}
        reply = await host.call("select_output", arguments, context)
        return reply if isinstance(reply, CallFailure) else selection(reply)

    async def recall(self, context: CallContext, message: JsonValue) -> JsonValue | CallFailure:
        host = self._hosts.get((context.node_id, "memory"))
        if host is None:
            return _missing(context.node_id)
        reply = await host.call("recall", {"message": message}, context)
        return reply if isinstance(reply, CallFailure) else recalled(reply)

    async def remember(
        self, context: CallContext, received: JsonValue, replied: JsonValue
    ) -> None | CallFailure:
        host = self._hosts.get((context.node_id, "memory"))
        if host is None:
            return _missing(context.node_id)
        arguments: dict[str, JsonValue] = {"received": received, "replied": replied}
        reply = await host.call("remember", arguments, context)
        return reply if isinstance(reply, CallFailure) else remembered(reply)

    async def close(self) -> None:
        """Stops every host at once within the shutdown budget; never raises."""
        with suppress(Exception):
            await asyncio.gather(*(host.stop() for host in self._hosts.values()))
        shutil.rmtree(self._directory, ignore_errors=True)


def _missing(node_id: str) -> CallFailure:
    return CallFailure("host_failed", f'No component host serves the node "{node_id}".')
