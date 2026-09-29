"""Durable launch intentions and OS identity are separate from invocation authority."""

from dataclasses import dataclass
from typing import Protocol, runtime_checkable

from ._runtime_ports import RunEnvironment


@dataclass(frozen=True)
class ProcessIdentity:
    pid: int
    created_at: float
    executable: str
    command: tuple[str, ...]
    marker: str
    workspace: str
    group: int
    session: int


@dataclass(frozen=True)
class OwnedLaunch:
    marker: str
    run_id: str
    runtime_id: str
    instance_id: str
    workspace: str
    identity: ProcessIdentity | None = None


class ProcessJournal(Protocol):
    def prepare(self, launch: OwnedLaunch) -> None: ...
    def started(self, identity: ProcessIdentity) -> None: ...
    def stopped(self, marker: str, reason: str) -> None: ...
    def unconfirmed(self, marker: str, reason: str) -> None: ...
    def pending(self) -> tuple[OwnedLaunch, ...]: ...
    def reconcile(self) -> None: ...
    def diagnostic(self, marker: str, payload_json: str) -> None: ...


@runtime_checkable
class OwnedRunEnvironment(RunEnvironment, Protocol):
    def bind_owner(self, run_id: str, runtime_id: str) -> None: ...
