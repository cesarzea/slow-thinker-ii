"""Stored runs and events, with their operator API and recording shapes."""

from dataclasses import dataclass
from datetime import UTC, datetime

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object


def rfc3339(at: datetime) -> str:
    """A timezone-aware time as UTC RFC 3339 with milliseconds: `2026-10-05T12:00:00.000Z`."""
    if at.utcoffset() is None:
        raise ValueError("A recorded time must be timezone-aware")
    moment = at.astimezone(UTC)
    return f"{moment:%Y-%m-%dT%H:%M:%S}.{moment.microsecond // 1000:03d}Z"


@dataclass(frozen=True)
class RunRecord:
    run_id: str
    graph_id: str
    version: int | None  # None for a change that was never activated
    change: int  # the change the run executed
    status: str  # starting, running, completed, stopped, failed or cancelled
    reason: str | None
    detail: str
    input: JsonValue
    created_at: datetime
    ended_at: datetime | None
    totals: JsonObject | None  # None until the run is finished

    def to_json(self) -> JsonObject:
        """The run summary of the operator API."""
        ended = None if self.ended_at is None else rfc3339(self.ended_at)
        return {
            "run_id": self.run_id,
            "graph_id": self.graph_id,
            "version": self.version,
            "change": self.change,
            "status": self.status,
            "reason": self.reason,
            "detail": self.detail,
            "created_at": rfc3339(self.created_at),
            "ended_at": ended,
            "totals": None if self.totals is None else json_object(self.totals),
        }


@dataclass(frozen=True)
class NewEvent:
    at: datetime
    elapsed_ms: int  # since the run was admitted
    kind: str
    evidence: str  # observed or reported
    node_id: str | None
    activation_id: str | None
    data: JsonObject


@dataclass(frozen=True)
class RecordedEvent:
    run_id: str
    seq: int  # 1, 2, 3… without gaps within the run
    at: datetime
    elapsed_ms: int
    kind: str
    evidence: str
    node_id: str | None
    activation_id: str | None
    data: JsonObject

    def to_json(self) -> JsonObject:
        """The envelope of the recording contract."""
        return {
            "run_id": self.run_id,
            "seq": self.seq,
            "at": rfc3339(self.at),
            "elapsed_ms": self.elapsed_ms,
            "kind": self.kind,
            "evidence": self.evidence,
            "node_id": self.node_id,
            "activation_id": self.activation_id,
            "data": json_object(self.data),
        }
