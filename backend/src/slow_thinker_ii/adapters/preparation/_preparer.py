"""Prepare one exact bundled graph using approved backend resources and immutable local evidence."""

import asyncio
import math
import subprocess
from collections.abc import Callable, Mapping
from contextlib import suppress
from pathlib import Path

from slow_thinker_ii.adapters.catalog import (
    BundledDefinitionStore,
    GraphRecord,
    InstalledGraphCompiler,
)
from slow_thinker_ii.adapters.installations import InstallationCatalog
from slow_thinker_ii.application import (
    ExecutionConfiguration,
    PreparationRejected,
    PreparedWorkflow,
    ProcessJournal,
    StartIntent,
    TariffStore,
)

from ._endpoints import ServiceEndpoints
from ._host_profiles import HostAdapter
from ._mcp_bindings import bind_mcp
from ._models import ResourceSettings
from ._planning import HostPlanner
from ._secrets import SecretSource
from ._selection import select_types
from ._tariffs import select_tariff
from ._workflow import WorkflowAssembly


class InstalledWorkflowPreparer:
    def __init__(
        self,
        definitions: BundledDefinitionStore,
        installations: InstallationCatalog,
        schemas: Path,
        descriptors: tuple[str, ...],
        configuration: Callable[[], ExecutionConfiguration | None],
        tariffs: TariffStore,
        secrets: SecretSource,
        endpoints: ServiceEndpoints,
        workspace: Path,
        adapters: Mapping[str, HostAdapter],
        wall: Callable[[], float],
        journal: ProcessJournal | None = None,
    ) -> None:
        if not workspace.is_absolute():
            raise ValueError("Preparation requires an absolute workspace")
        self._definitions, self._installations, self._schemas = definitions, installations, schemas
        self._descriptors, self._configuration = descriptors, configuration
        self._tariffs, self._secrets, self._endpoints = tariffs, secrets, endpoints
        self._workspace, self._adapters, self._wall = workspace, dict(adapters), wall
        self._journal = journal

    async def prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow:
        worker = asyncio.create_task(asyncio.to_thread(self._prepare, intent, runtime_id))
        try:
            return await asyncio.shield(worker)
        except asyncio.CancelledError:
            with suppress(Exception):
                await asyncio.shield(worker)
            raise

    def _prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow:
        configuration = self._configuration()
        if configuration is None or configuration.revision != intent.configuration_revision:
            raise PreparationRejected("configuration_unavailable")
        try:
            return self._configured(intent, runtime_id, configuration)
        except PreparationRejected:
            raise
        except (ValueError, KeyError) as error:
            raise PreparationRejected("invalid_graph_or_resource_configuration") from error
        except (OSError, RuntimeError, subprocess.TimeoutExpired) as error:
            raise PreparationRejected("component_preparation_unavailable") from error

    def _configured(
        self, intent: StartIntent, runtime_id: str, configuration: ExecutionConfiguration
    ) -> PreparedWorkflow:
        now = self._wall()
        if isinstance(now, bool) or not math.isfinite(now):
            raise PreparationRejected("invalid_preparation_clock")
        graph_json = self._definitions.definition(intent.graph_id, intent.graph_revision)
        graph = GraphRecord.model_validate_json(graph_json)
        if graph.limits_profile != configuration.limits.revision:
            raise PreparationRejected("limits_profile_mismatch")
        settings = ResourceSettings.model_validate_json(configuration.resources_json)
        types = select_types(settings, self._descriptors)
        tariff = select_tariff(self._tariffs)
        planner = HostPlanner(self._adapters, self._endpoints, self._secrets)
        hosts = planner.configure(graph, configuration.limits, settings, tariff, now)
        compiler = InstalledGraphCompiler(
            self._installations, self._schemas, types, configuration.limits.startup_seconds
        )
        configs = {
            key: host.config_json for key, host in hosts.items() if host.config_json is not None
        }
        installed = compiler.compile(graph_json, intent.input_json, configs)
        hosts = bind_mcp(installed, hosts, self._endpoints.gateway, configuration.limits)
        assembly = WorkflowAssembly(
            self._installations, self._workspace, installed, hosts, tariff, self._journal
        )
        return assembly.prepare(intent, configuration, runtime_id)
