"""Only the verified registered environment may host an admitted installed component."""

import asyncio
from collections.abc import AsyncIterator
from contextlib import AsyncExitStack, asynccontextmanager
from dataclasses import dataclass, field
from pathlib import Path

from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.contracts import OperationContract

from ._connection import ComponentConnection, ComponentProcess
from ._launch import ProcessLaunch
from ._secrets import ProcessSecret


@dataclass(frozen=True)
class HostSettings:
    bootstrap: Path
    workspace: Path
    startup_seconds: float
    shutdown_seconds: float
    max_message_bytes: int
    secrets: tuple[ProcessSecret, ...] = field(default=(), repr=False)


class InstalledProcess(ComponentProcess):
    def __init__(
        self,
        catalog: InstallationCatalog,
        identity: str,
        type_id: str,
        type_version: str,
        settings: HostSettings,
        operations: tuple[OperationContract, ...],
    ) -> None:
        resolution, python = catalog.runtime(identity)
        registration = resolution.registration
        if (registration.type_id, registration.type_version) != (type_id, type_version):
            raise ValueError("Installed component identity differs from the admitted type")
        self._catalog, self._identity = catalog, identity
        self._snapshot = resolution.model_dump_json()
        self._settings = settings
        launch = ProcessLaunch(
            python,
            registration.entry_point.split(":")[0],
            settings.bootstrap,
            settings.workspace,
            settings.startup_seconds,
            settings.shutdown_seconds,
            settings.max_message_bytes,
            settings.secrets,
        )
        super().__init__(launch, operations)

    def installation_json(self) -> str:
        return self._snapshot

    def _verify(self) -> None:
        if self._catalog.verify(self._identity).model_dump_json() != self._snapshot:
            raise ValueError("The admitted installation record changed")

    @asynccontextmanager
    async def connect(self) -> AsyncIterator[ComponentConnection]:
        try:
            async with AsyncExitStack() as stack:
                async with asyncio.timeout(self._settings.startup_seconds):
                    await asyncio.to_thread(self._verify)
                    connection = await stack.enter_async_context(super().connect())
                yield connection
        finally:
            async with asyncio.timeout(self._settings.shutdown_seconds):
                await asyncio.to_thread(self._verify)
