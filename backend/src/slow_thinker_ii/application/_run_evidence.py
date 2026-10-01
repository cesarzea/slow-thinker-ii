"""Durable evidence derives run and call identity exclusively from active authority."""

from slow_thinker_ii.access import AccessDenied, CallAuthority, CallContext
from slow_thinker_ii.contracts import JsonObject, encode_json

from ._component_reports import component_report, redact
from ._run_ports import RecordingError, RunStore


class RunEvidence:
    def __init__(self, authority: CallAuthority, store: RunStore, limit: int) -> None:
        self._authority, self._store, self._limit = authority, store, limit
        self._reports: dict[str, int] = {}
        self._rejections: dict[str, int] = {}

    def reject(self, grant: str, requested_operation: str, reason: str) -> None:
        try:
            context = self._authority.context(grant)
        except AccessDenied:
            return
        count = self._rejections.get(context.call_id, 0) + 1
        self._rejections[context.call_id] = count
        if count >= 100:
            self._close_diagnostics(context)
            return
        self.record(
            context,
            "call.rejected",
            {
                "requested_operation": redact(requested_operation[:256], grant),
                "reason": redact(reason[:128], grant),
                "stage": "gateway",
                "caller": context.target.instance,
                "activation_id": context.activation_id,
            },
        )

    def report(self, grant: str, report_json: str) -> None:
        context = self._authority.context(grant)
        scope = context.activation_id or context.call_id
        try:
            report = component_report(report_json, grant, self._limit // 2)
            if self._reports.get(scope, 0) >= 100:
                raise ValueError("report_count_limit")
        except ValueError as error:
            self.reject(grant, "platform.report", str(error))
            raise
        report.update(
            {"component": context.target.instance, "activation_id": context.activation_id}
        )
        self.record(context, "component.reported", report)
        self._reports[scope] = self._reports.get(scope, 0) + 1

    def record(self, context: CallContext, event: str, payload: JsonObject) -> None:
        try:
            with self._store.begin() as transaction:
                saved = transaction.call(context.call_id)
                if (
                    saved.prepared.context != context
                    or transaction.run(context.run_id).state != "running"
                ):
                    raise AccessDenied("run_closed")
                transaction.event(context.run_id, event, context.call_id, encode_json(payload))
        except RecordingError:
            self._authority.stop()
            raise

    def _close_diagnostics(self, context: CallContext) -> None:
        try:
            with self._store.begin() as transaction:
                transaction.stop(context.run_id, "gateway_rejection_limit")
        finally:
            self._authority.stop()
