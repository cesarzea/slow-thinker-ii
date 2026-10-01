"""Durable launch intentions and OS identity are separate from invocation authority."""

from abc import abstractmethod
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
    @abstractmethod
    def prepare(self, launch: OwnedLaunch) -> None:
        raise NotImplementedError

    @abstractmethod
    def started(self, identity: ProcessIdentity) -> None:
        raise NotImplementedError

    @abstractmethod
    def stopped(self, marker: str, reason: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def unconfirmed(self, marker: str, reason: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def pending(self) -> tuple[OwnedLaunch, ...]:
        raise NotImplementedError

    @abstractmethod
    def reconcile(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def diagnostic(self, marker: str, payload_json: str) -> None:
        raise NotImplementedError


@runtime_checkable
class OwnedRunEnvironment(RunEnvironment, Protocol):
    @abstractmethod
    def bind_owner(self, run_id: str, runtime_id: str) -> None:
        raise NotImplementedError
