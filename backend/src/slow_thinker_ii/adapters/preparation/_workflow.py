"""Assemble an admitted workflow without starting its component processes."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from slow_thinker_ii.adapters.catalog import InstalledPlan
from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.adapters.process import HostLimits, InstalledGraphEnvironment
from slow_thinker_ii.application import (
    ExecutionConfiguration,
    PreparationRejected,
    PreparedStart,
    PreparedWorkflow,
    SequenceProgram,
    StartIntent,
    sequence_access,
)

from ._host_profiles import HostProfile
from ._snapshots import snapshot
from ._tariffs import SelectedTariff


@dataclass(frozen=True)
class WorkflowAssembly:
    installations: InstallationCatalog
    workspace: Path
    installed: InstalledPlan
    hosts: dict[str, HostProfile]
    tariff: SelectedTariff | None

    def prepare(
        self, intent: StartIntent, configuration: ExecutionConfiguration, runtime_id: str
    ) -> PreparedWorkflow:
        deadlines = [
            host.admit_before for host in self.hosts.values() if host.admit_before is not None
        ]
        deadline = min(deadlines) if deadlines else None
        prepared = PreparedStart(
            intent,
            configuration,
            runtime_id,
            snapshot(self.installed, self.hosts, self.tariff),
            deadline,
        )
        if len(prepared.record_json().encode()) > configuration.limits.max_payload_bytes:
            raise PreparationRejected("snapshot_limit")
        return PreparedWorkflow(
            prepared,
            sequence_access(self.installed.plan),
            self.environment(configuration),
            SequenceProgram(self.installed.plan),
            tuple(model for host in self.hosts.values() for model in host.models),
        )

    def environment(self, configuration: ExecutionConfiguration) -> InstalledGraphEnvironment:
        limits = configuration.limits
        return InstalledGraphEnvironment(
            self.installations,
            self.installed,
            self.workspace / uuid4().hex,
            {key: host.binding for key, host in self.hosts.items()},
            HostLimits(limits.startup_seconds, limits.shutdown_seconds, limits.max_payload_bytes),
        )
