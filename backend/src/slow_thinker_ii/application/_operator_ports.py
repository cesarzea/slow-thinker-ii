"""Operator composition depends on command storage and trusted preparation, never HTTP objects."""

from dataclasses import dataclass
from typing import Protocol

from slow_thinker_ii.access import AccessPolicy

from ._native_records import ModelBinding
from ._operator_records import CommandResult, PreparedStart, StartIntent
from ._runtime_ports import RunEnvironment, RunProgram


class OperatorCommandStore(Protocol):
    def create_session(self, command_id: str, name: str) -> CommandResult: ...
    def resolve(self, command_id: str, intent: StartIntent) -> CommandResult | None: ...
    def admit(self, command_id: str, prepared: PreparedStart) -> CommandResult: ...
    def reject(self, command_id: str, intent: StartIntent, reason: str) -> CommandResult: ...
    def stop(self, command_id: str, run_id: str) -> CommandResult: ...
    def withdraw(self, command_id: str) -> CommandResult: ...


@dataclass(frozen=True)
class PreparedWorkflow:
    start: PreparedStart
    policy: AccessPolicy
    environment: RunEnvironment
    program: RunProgram
    models: tuple[ModelBinding, ...] = ()

    def require_identity(self, intent: StartIntent, runtime_id: str) -> None:
        if self.start.intent != intent or self.start.runtime_id != runtime_id:
            raise PreparationRejected("preparation_identity_mismatch")


class WorkflowPreparer(Protocol):
    async def prepare(self, intent: StartIntent, runtime_id: str) -> PreparedWorkflow: ...


class PreparationRejected(ValueError):
    def __init__(self, code: str) -> None:
        self.code = code
        super().__init__(code)


class CoordinatorUnavailable(RuntimeError):
    """This backend cannot accept another command at this time."""


@dataclass(frozen=True)
class CoordinatorShutdown:
    commands: tuple[str, ...]
    preparations: tuple[str, ...]
    runs: tuple[str, ...]
