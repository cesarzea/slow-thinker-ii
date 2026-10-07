"""Component reports, recorded as reported evidence for the activation of their grant."""

from slow_thinker_ii.contracts import JsonValue, encode_json, json_value

from ._errors import InvalidGrant, InvalidReport
from ._runs import RunService

REPORT_KINDS = frozenset({"step", "progress", "state", "explanation", "reasoning"})
MAX_CONTENT_BYTES = 65_536


class ReportService:
    def __init__(self, runs: RunService) -> None:
        self._runs = runs

    def report(self, grant: str, kind: str, content: JsonValue) -> None:
        """Raises `InvalidGrant` for an unknown or expired grant, `InvalidReport` otherwise."""
        call = self._runs.active_call(grant)
        if call is None:
            raise InvalidGrant()
        if kind not in REPORT_KINDS:
            raise InvalidReport(
                f"Report kind “{kind}” is not one of {', '.join(sorted(REPORT_KINDS))}."
            )
        value = json_value(content)
        if len(encode_json(value).encode("utf-8")) > MAX_CONTENT_BYTES:
            raise InvalidReport(f"Report content exceeds {MAX_CONTENT_BYTES} bytes.")
        caller = call.caller
        data = {"kind": kind, "content": value}
        call.run.journal.report(data, node_id=caller.node_id, activation_id=caller.activation_id)
