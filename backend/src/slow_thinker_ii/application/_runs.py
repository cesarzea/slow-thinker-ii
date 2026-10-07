"""Runs: admission, background execution, stops, queries, recovery and shutdown."""

import asyncio
import uuid
from collections.abc import Callable

from slow_thinker_ii.access import Grants
from slow_thinker_ii.accounting import Scope, format_usd
from slow_thinker_ii.catalog import Catalog
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.graphs import RunPlan

from ._active import ActiveCall, ActiveRun, CallGrants, caller_component
from ._budgets import budget_detail, budget_reason
from ._errors import TooManyRuns
from ._execution import RunExecution
from ._journal import RunJournal
from ._ports import Clock, GraphStore, HostLauncher, Ledger, RunStore
from ._records import RunRecord
from ._recovery import Recovery
from ._run_plans import run_plan
from ._run_queries import RunQueries
from ._values import BudgetLimits, RunSettings
from ._views import EventPage, RunView

OPERATOR_STOP = "The operator stopped the run."
SHUTDOWN = "The platform shut down before the run finished."


class RunService:
    def __init__(
        self,
        *,
        graphs: GraphStore,
        runs: RunStore,
        ledger: Ledger,
        launcher: HostLauncher,
        grants: Grants,
        clock: Clock,
        catalog: Callable[[], Catalog],
        budgets: BudgetLimits,
        settings: RunSettings | None = None,
    ) -> None:
        self._graphs, self._store, self._grants = graphs, runs, grants
        self._clock, self._catalog, self._budgets = clock, catalog, budgets
        self._settings = settings = settings or RunSettings()
        self._active: dict[str, ActiveRun] = {}
        self._queries = RunQueries(runs, self._active)
        self._recovery = Recovery(runs, ledger, clock, self._queries)
        seconds = settings.max_activation_seconds
        self._execution = RunExecution(runs, launcher, grants, clock, seconds, self._active)

    async def start(
        self,
        graph_id: str,
        version: int | None,
        input: JsonValue = None,
        *,
        change: int | None = None,
    ) -> str:
        """Admits a run of a version, or of a change when `version` is None, and continues in
        the background; `None` input is the Trigger's message."""
        plan, executed = run_plan(self._graphs, self._catalog, graph_id, version, change)
        if len(self._active) >= self._settings.max_active_runs:
            raise TooManyRuns(self._settings.max_active_runs)
        trigger = plan.node(plan.trigger_id).host.config.get("message")
        message = trigger if input is None else input
        run_id = uuid.uuid4().hex
        now = self._clock.now()
        record = RunRecord(
            run_id, graph_id, plan.version, executed, "starting", None, "", message, now, None, None
        )
        self._store.create(record)
        journal = RunJournal(run_id, self._store, self._clock)
        journal.record("run.started", self._started(plan, executed, message))
        run = ActiveRun(run_id, plan, journal, CallGrants(self._grants, self._clock))
        self._active[run_id] = run
        run.task = asyncio.create_task(self._execution.execute(run, message))
        return run_id

    def stop(self, run_id: str) -> str:
        """Requests cancellation; returns the current status, or the final one when finished."""
        run = self._active.get(run_id)
        if run is not None:
            run.stop("cancelled", OPERATOR_STOP)
        return self._queries.record(run_id).status

    def stop_for_budget(self, run_id: str, scope: Scope) -> None:
        run = self._active.get(run_id)
        if run is not None:
            run.stop(budget_reason(scope.kind), budget_detail(scope))

    def run(self, run_id: str) -> RunView:
        return self._queries.view(run_id)

    def runs(self, graph_id: str | None, limit: int) -> tuple[RunRecord, ...]:
        return self._queries.runs(graph_id, limit)

    def events(self, run_id: str, after: int, limit: int) -> EventPage:
        return self._queries.events(run_id, after, limit)

    def recover(self) -> None:
        self._recovery.recover()

    async def shutdown(self) -> None:
        """Stops every active run as cancelled and waits until each has finished."""
        runs = list(self._active.values())
        for run in runs:
            run.stop("cancelled", SHUTDOWN)
        await asyncio.gather(*(run.task for run in runs if run.task), return_exceptions=True)

    def active_call(self, grant: str) -> ActiveCall | None:
        """The active call a grant identifies; used by `LlmGateway` and `ReportService`."""
        caller = self._grants.resolve(grant)
        run = None if caller is None else self._active.get(caller.run_id)
        if caller is None or run is None:
            return None
        component = caller_component(run.plan, caller)
        return ActiveCall(caller, component, run, run.grants.remaining(caller))

    def _started(self, plan: RunPlan, change: int, message: JsonValue) -> JsonObject:
        limits = plan.limits
        return {
            "graph_id": plan.graph_id,
            "graph_version": plan.version,
            "graph_change": change,
            "input": message,
            "limits": {
                "max_activations": limits.max_activations,
                "max_running_nodes": limits.max_running_nodes,
                "time_limit_seconds": limits.time_limit_seconds,
                "budget_usd": format_usd(limits.budget_nanos),
            },
            "budgets": {
                "run_usd": format_usd(limits.budget_nanos),
                "day_usd": format_usd(self._budgets.daily_nanos),
                "month_usd": format_usd(self._budgets.monthly_nanos),
            },
        }
