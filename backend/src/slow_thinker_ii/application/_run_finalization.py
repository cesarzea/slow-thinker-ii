"""Close transient authority before committing a terminal execution decision."""

from collections.abc import Callable

from slow_thinker_ii.access import AccessDenied, CallAuthority

from ._run_ports import RunStore
from ._run_records import RunRecord


class RunFinalization:
    def __init__(
        self,
        authority: CallAuthority,
        store: RunStore,
        run_id: str,
        runtime_id: str,
        clock: Callable[[], float],
    ) -> None:
        self._authority, self._store = authority, store
        self._run, self._runtime, self._clock = run_id, runtime_id, clock

    def finish(self, output_json: str | None = None) -> RunRecord:
        executing = bool(self._authority.stop())
        with self._store.begin() as transaction:
            return transaction.finish_run(
                self._run, self._runtime, self._clock(), output_json, executing=executing
            )

    def cleanup(self, payload_json: str) -> None:
        with self._store.begin() as transaction:
            if transaction.run(self._run).runtime_id != self._runtime:
                raise AccessDenied("runtime_mismatch")
            transaction.event(self._run, "run.cleanup", None, payload_json)
