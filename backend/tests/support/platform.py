"""The step 1 use cases composed over the in-memory fakes, as `bootstrap` composes the real ones."""

from collections.abc import Mapping, Sequence

from slow_thinker_ii.access import Grants
from slow_thinker_ii.application import (
    GraphLibrary,
    LlmGateway,
    ReportService,
    RunRecord,
    RunService,
    RunSettings,
    UsageService,
)
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import RunPlan

from .clock import FakeClock
from .components import ComponentHosts
from .configuration import budget_limits, llm_models
from .examples import graph_document, step_one_catalog
from .graph_store import MemoryGraphStore
from .hosts import Gate
from .launcher import FakeHostLauncher, HostsFactory
from .ledger import MemoryLedger
from .providers import ScriptedProvider, Step
from .run_store import MemoryRunStore


class Platform:
    """Every use case over fakes. Package nodes are `ComponentHosts` unless `hosts` is given;
    `hold`, when set before a run starts, holds its LLM Call activations until it opens."""

    def __init__(
        self,
        *,
        steps: Mapping[str, Sequence[Step]] | None = None,
        hosts: HostsFactory | None = None,
        settings: RunSettings | None = None,
    ) -> None:
        self.clock = FakeClock()
        self.graph_store, self.run_store = MemoryGraphStore(), MemoryRunStore()
        self.ledger = MemoryLedger()
        self.grants = Grants(self.clock.monotonic)
        self.provider = ScriptedProvider(self.clock, steps)
        self.hold: Gate | None = None
        self.hosts: list[ComponentHosts] = []
        self.launcher = FakeHostLauncher(hosts or self._component_hosts)
        self.catalog, self.budgets = step_one_catalog(), budget_limits()
        self.library = GraphLibrary(self.graph_store, lambda: self.catalog, self.clock)
        self.runs = self._run_service(settings)
        self.gateway = LlmGateway(
            runs=self.runs,
            ledger=self.ledger,
            provider=self.provider,
            models=llm_models(),
            budgets=self.budgets,
            clock=self.clock,
        )
        self.reports = ReportService(self.runs)
        self.usage = UsageService(self.ledger, self.budgets, self.clock)

    def saved(self, document: JsonObject | str) -> str:
        """Creates a graph from a journey (by name) or a document and activates its change 1
        as version 1; returns the graph identifier."""
        source = graph_document(document) if isinstance(document, str) else document
        graph_id, _, change = self.library.create(source)
        self.library.activate(graph_id, change)
        return graph_id

    async def started(self, document: JsonObject | str, message: JsonValue = None) -> str:
        return await self.runs.start(self.saved(document), 1, message)

    async def completed(self, document: JsonObject | str, message: JsonValue = None) -> RunRecord:
        return await self.finish(await self.started(document, message))

    async def finish(self, run_id: str) -> RunRecord:
        """Waits for `run.finished`, then for the run's cleanup through `shutdown`."""
        record = await self.run_store.finished(run_id)
        await self.runs.shutdown()
        return record

    def _run_service(self, settings: RunSettings | None) -> RunService:
        return RunService(
            graphs=self.graph_store,
            runs=self.run_store,
            ledger=self.ledger,
            launcher=self.launcher,
            grants=self.grants,
            clock=self.clock,
            catalog=lambda: self.catalog,
            budgets=self.budgets,
            settings=settings,
        )

    def _component_hosts(self, plan: RunPlan) -> ComponentHosts:
        hosts = ComponentHosts(plan, lambda: self.gateway, self.hold)
        self.hosts.append(hosts)
        return hosts
