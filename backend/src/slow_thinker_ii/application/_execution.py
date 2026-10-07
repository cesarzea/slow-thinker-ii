"""The background task of a run: launch hosts, run the engine, record `run.finished`, clean up."""

from collections.abc import MutableMapping
from contextlib import suppress
from dataclasses import dataclass

from slow_thinker_ii.access import Grants
from slow_thinker_ii.contracts import JsonObject, JsonValue
from slow_thinker_ii.engine import RunEngine

from ._active import ActiveRun
from ._errors import StartupFailed
from ._ports import Clock, HostLauncher, RunStore


@dataclass(frozen=True)
class Ending:
    status: str
    reason: str | None
    detail: str
    activations: int
    messages: int


class RunExecution:
    def __init__(
        self,
        store: RunStore,
        launcher: HostLauncher,
        grants: Grants,
        clock: Clock,
        max_activation_seconds: int,
        active: MutableMapping[str, ActiveRun],
    ) -> None:
        self._store = store
        self._launcher = launcher
        self._grants = grants
        self._clock = clock
        self._max_activation_seconds = max_activation_seconds
        self._active = active

    async def execute(self, run: ActiveRun, message: JsonValue) -> None:
        """Never raises: unexpected errors end the run `failed` with `internal_error`."""
        try:
            try:
                ending = await self._ending(run, message)
            except Exception as error:
                detail = f"The run failed unexpectedly: {type(error).__name__}: {error}"
                ending = Ending("failed", "internal_error", detail, 0, 0)
            await run.settle_calls()
            with suppress(Exception):
                self._finish(run, ending)
        finally:
            await self._release(run)

    async def _ending(self, run: ActiveRun, message: JsonValue) -> Ending:
        try:
            hosts = await self._launcher.launch(run.run_id, run.plan, run.journal)
        except StartupFailed as error:
            return Ending("failed", "startup_failed", str(error), 0, 0)
        run.hosts = hosts
        run_engine = RunEngine(
            run.run_id,
            run.plan,
            hosts,
            run.journal,
            run.grants,
            self._clock,
            max_activation_seconds=self._max_activation_seconds,
        )
        run.attach(run_engine)
        outcome = await run_engine.run(message)
        return Ending(
            outcome.status, outcome.reason, outcome.detail, outcome.activations, outcome.messages
        )

    def _finish(self, run: ActiveRun, ending: Ending) -> None:
        journal = run.journal
        totals = journal.totals.document(journal.elapsed_ms(), ending.activations, ending.messages)
        data: JsonObject = {
            "status": ending.status,
            "reason": ending.reason,
            "detail": ending.detail,
            "totals": totals,
            "dropped": journal.totals.dropped,
        }
        journal.record("run.finished", data)
        status, reason, detail = ending.status, ending.reason, ending.detail
        self._store.finish(run.run_id, status, reason, detail, totals, self._clock.now())

    async def _release(self, run: ActiveRun) -> None:
        with suppress(Exception):
            if run.hosts is not None:
                await run.hosts.close()
        self._grants.revoke_run(run.run_id)
        self._active.pop(run.run_id, None)
