"""Launch the installed participants of a compiled graph only after all bindings validate."""

import asyncio
import re
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager
from pathlib import Path

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.catalog import InstalledPlan
from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.application import OperationPort

from ._fleet import ProcessFleet, ProcessHost
from ._graph_bindings import HostBinding, HostLimits
from ._graph_hosts import build_host, validate_billing


class InstalledGraphEnvironment:
    def __init__(
        self,
        catalog: InstallationCatalog,
        installed: InstalledPlan,
        workspace: Path,
        bindings: Mapping[str, HostBinding],
        limits: HostLimits,
    ) -> None:
        if not workspace.is_absolute():
            raise ValueError("A graph runtime needs an absolute workspace")
        configurations = installed.configurations
        identities = {item.instance_id for item in configurations}
        if len(identities) != len(configurations) or any(
            not re.fullmatch(r"[a-z][a-z0-9_.-]*", identity) for identity in identities
        ):
            raise ValueError("Graph host identities must be unique and path-safe")
        if identities != {item.instance_id for item in installed.plan.instances}:
            raise ValueError("Installed configurations do not match the compiled graph")
        if set(bindings) != identities:
            raise ValueError("Provide exactly one trusted host binding per graph instance")
        for config in configurations:
            validate_billing(config, bindings[config.instance_id])
        self._catalog, self._configs, self._workspace = catalog, configurations, workspace
        self._bindings, self._limits = dict(bindings), limits
        self._fleet: ProcessFleet | None = None
        self._used = False

    @asynccontextmanager
    async def open(
        self, deadline: float
    ) -> AsyncIterator[Mapping[OperationAddress, OperationPort]]:
        if self._used:
            raise RuntimeError("A graph environment cannot be reused")
        self._used = True
        hosts: list[ProcessHost] = []
        async with asyncio.timeout_at(deadline):
            for config in self._configs:
                host = await asyncio.to_thread(
                    build_host,
                    self._catalog,
                    config,
                    self._bindings[config.instance_id],
                    self._workspace,
                    self._limits,
                )
                hosts.append(host)
        self._fleet = ProcessFleet(tuple(hosts))
        async with self._fleet.open(deadline) as operations:
            yield operations

    def report(self) -> str:
        return "[]" if self._fleet is None else self._fleet.report()
