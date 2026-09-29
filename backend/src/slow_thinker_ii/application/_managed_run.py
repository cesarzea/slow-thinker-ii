"""One owner keeps readiness, graph work, terminal state and cleanup in the same lifetime."""

import asyncio
import json
import math
from collections.abc import Callable, Mapping

from slow_thinker_ii.access import AccessDenied, CallAuthority, OperationAddress
from slow_thinker_ii.contracts import JsonObject
from slow_thinker_ii.execution import ActivationLimitReached

from ._call_runner import ManagedCalls
from ._dispatch_ports import ManagedResult, OperationPort
from ._run_admission import RunAdmission
from ._run_evidence import RunEvidence
from ._run_finalization import RunFinalization
from ._run_ports import RecordingError
from ._run_records import RunRecord
from ._runtime_ports import RunEnvironment, RunProgram


class ManagedRun:
    def __init__(
        self,
        authority: CallAuthority,
        admission: RunAdmission,
        finalization: RunFinalization,
        environment: RunEnvironment,
        deadline: float,
        cleanup_seconds: float,
        evidence: RunEvidence | None = None,
    ) -> None:
        if (
            isinstance(deadline, bool)
            or isinstance(cleanup_seconds, bool)
            or not math.isfinite(deadline)
            or not math.isfinite(cleanup_seconds)
            or cleanup_seconds <= 0
        ):
            raise ValueError("Finite run and cleanup bounds are required")
        self._authority, self._admission, self._finalization = authority, admission, finalization
        self._environment, self._deadline, self._cleanup = environment, deadline, cleanup_seconds
        self._calls: ManagedCalls | None = None
        self._used = False
        self._cancel_startup: Callable[[], bool] | None = None
        self._failure: str | None = None
        self._evidence = evidence

    async def execute(self, program: RunProgram) -> RunRecord:
        self._begin()
        try:
            self._admission.check_start()
            async with self._environment.open(self._deadline) as operations:
                return await self._perform(program, operations)
        except asyncio.CancelledError:
            self._cancel_startup = None
            self._abort("runtime_shutdown")
            raise
        except RecordingError:
            self._failure = "RecordingError"
            self._authority.stop()
            raise
        except Exception as error:
            self._cancel_startup = None
            self._failure = type(error).__name__
            reason = "run_deadline" if isinstance(error, TimeoutError) else "startup_failure"
            return self._abort(reason if self._calls is None else "execution_failure")
        finally:
            self._cancel_startup = None
            self._finalization.cleanup(self._cleanup_report())

    def _begin(self) -> None:
        if self._used:
            raise RuntimeError("A managed run cannot be restarted")
        self._used = True
        owner: asyncio.Task[object] | None = asyncio.current_task()
        self._cancel_startup = lambda: False if owner is None else owner.cancel()

    async def _perform(
        self, program: RunProgram, operations: Mapping[OperationAddress, OperationPort]
    ) -> RunRecord:
        self._cancel_startup = None
        self._calls = ManagedCalls(self._authority, self._admission, operations, self._evidence)
        try:
            self._admission.start()
            async with asyncio.timeout_at(self._deadline):
                output = await program.execute(self._calls)
            return self._finalization.finish(output)
        except ActivationLimitReached:
            self.stop("activation_limit_reached")
            raise
        except asyncio.CancelledError:
            self.stop("runtime_shutdown")
            raise
        except Exception as error:
            self.stop("run_deadline" if isinstance(error, TimeoutError) else "operation_failed")
            raise
        finally:
            await self._calls.close(self._cleanup)

    async def invoke(self, grant: str, alias: str, arguments_json: str) -> ManagedResult:
        if self._calls is None:
            raise AccessDenied("run_not_ready")
        return await self._calls.invoke(grant, alias, arguments_json)

    def stop(self, reason: str = "operator_stop") -> tuple[str, ...]:
        if self._calls is None:
            try:
                return self._admission.stop(reason)
            finally:
                if self._cancel_startup is not None:
                    self._cancel_startup()
        return self._calls.stop(reason)

    def _abort(self, reason: str) -> RunRecord:
        self.stop(reason)
        return self._finalization.finish()

    def _cleanup_report(self) -> str:
        pending = () if self._calls is None else self._calls.pending()
        payload: JsonObject = {
            "environment_json": self._environment.report(),
            "pending_calls": [context.call_id for context in pending],
            "error_type": self._failure,
        }
        return json.dumps(payload)
