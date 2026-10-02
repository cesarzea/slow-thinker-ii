"""Trusted execution dependencies are composed separately from browser-supplied intentions."""

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol

from slow_thinker_ii.adapters.http import OperatorAccess
from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.adapters.preparation import (
    InstalledWorkflowPreparer,
    SecretSource,
    ServiceEndpoints,
    standard_host_adapters,
)
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteOperatorQueries,
    SqliteOperatorStore,
    SqliteProcessJournal,
    SqliteRunStore,
    SqliteTariffStore,
)
from slow_thinker_ii.application import ExecutionConfiguration, ExecutionCoordinator

from ._library import experiment_library


@dataclass(frozen=True)
class ExecutionServices:
    configuration: ExecutionConfiguration
    coordinator: ExecutionCoordinator
    commands: SqliteOperatorStore
    queries: SqliteOperatorQueries
    access: OperatorAccess

    async def close(self) -> bool:
        pending = await self.coordinator.close()
        return not (pending.commands or pending.preparations or pending.runs)


class ExecutionComposition(Protocol):
    def build(self, database: SqliteDatabase, root: Path) -> ExecutionServices: ...


@dataclass(frozen=True)
class ExecutionSetup:
    configuration: ExecutionConfiguration
    installations: InstallationCatalog
    descriptors: tuple[str, ...]
    endpoints: ServiceEndpoints
    secrets: SecretSource = field(repr=False)
    access: OperatorAccess = field(repr=False)
    cursor_key: bytes = field(repr=False)
    workspace: Path
    preparation_seconds: float
    maximum_commands: int

    def build(self, database: SqliteDatabase, root: Path) -> ExecutionServices:
        limits = self.configuration.limits
        commands = SqliteOperatorStore(database, limits.max_payload_bytes)
        preparer = self.preparer(database, root, commands)
        coordinator = ExecutionCoordinator(
            commands,
            SqliteRunStore(database, limits.max_payload_bytes),
            preparer,
            time.monotonic,
            self.preparation_seconds,
            limits.shutdown_seconds,
            self.maximum_commands,
        )
        return ExecutionServices(
            self.configuration,
            coordinator,
            commands,
            SqliteOperatorQueries(database, self.cursor_key),
            self.access,
        )

    def preparer(
        self, database: SqliteDatabase, root: Path, commands: SqliteOperatorStore
    ) -> InstalledWorkflowPreparer:
        return InstalledWorkflowPreparer(
            experiment_library(database, root),
            self.installations,
            root / "docs/contracts/schemas",
            self.descriptors,
            commands.profile,
            SqliteTariffStore(database),
            self.secrets,
            self.endpoints,
            self.workspace,
            standard_host_adapters(),
            time.time,
            SqliteProcessJournal(database, self.configuration.limits.max_payload_bytes),
        )
