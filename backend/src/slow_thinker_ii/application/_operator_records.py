"""Comparable operator intentions and durable receipts contain no invocation grants."""

import math
from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ._limits_profile import LimitsProfile

type CommandKind = Literal["session", "start", "stop"]
type CommandDisposition = Literal["accepted", "rejected", "already_terminal", "withdrawn"]


class CommandConflict(ValueError):
    """An existing command identity cannot be used for another intention."""


@dataclass(frozen=True)
class CommandReceipt:
    command_id: str
    kind: CommandKind
    disposition: CommandDisposition
    target_id: str | None = None
    reason: str | None = None


@dataclass(frozen=True)
class CommandResult:
    receipt: CommandReceipt
    replayed: bool


@dataclass(frozen=True)
class StartIntent:
    session_id: str
    graph_id: str
    graph_revision: str
    configuration_revision: str
    input_json: str

    def __post_init__(self) -> None:
        if not all(
            (self.session_id, self.graph_id, self.graph_revision, self.configuration_revision)
        ):
            raise ValueError("Start requires exact session, graph and configuration identities")
        object.__setattr__(
            self, "input_json", encode_json(json_object(decode_json(self.input_json)))
        )

    def to_json(self) -> str:
        return encode_json(
            {
                "session_id": self.session_id,
                "graph_id": self.graph_id,
                "graph_revision": self.graph_revision,
                "configuration_revision": self.configuration_revision,
                "input": decode_json(self.input_json),
            }
        )


@dataclass(frozen=True)
class ExecutionConfiguration:
    revision: str
    limits: LimitsProfile
    resources_json: str

    def __post_init__(self) -> None:
        if not self.revision:
            raise ValueError("An execution configuration needs a revision")
        frozen = encode_json(json_object(decode_json(self.resources_json)))
        object.__setattr__(self, "resources_json", frozen)

    def to_json(self) -> str:
        return encode_json(
            {
                "revision": self.revision,
                "limits": decode_json(self.limits.to_json()),
                "resources_json": self.resources_json,
            }
        )


@dataclass(frozen=True)
class PreparedStart:
    intent: StartIntent
    configuration: ExecutionConfiguration
    runtime_id: str
    snapshot_json: str
    admit_before: float | None = None

    def __post_init__(self) -> None:
        if not self.runtime_id or self.configuration.revision != self.intent.configuration_revision:
            raise ValueError("Prepared start must match the selected runtime and limits revision")
        json_object(decode_json(self.snapshot_json))
        if self.admit_before is not None and (
            isinstance(self.admit_before, bool) or not math.isfinite(self.admit_before)
        ):
            raise ValueError("A finite preparation admission deadline is required")

    def record_json(self) -> str:
        return encode_json(
            {
                "intent": decode_json(self.intent.to_json()),
                "configuration": decode_json(self.configuration.to_json()),
                "execution": decode_json(self.snapshot_json),
                "admit_before": self.admit_before,
            }
        )


@dataclass(frozen=True)
class SavedSession:
    session_id: str
    name: str
    created_at: float
