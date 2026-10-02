"""Workspace use cases consume injected discovery and durable command ports."""

from typing import Protocol

from slow_thinker_ii.contracts import JsonObject

from .._limits_profile import LimitsProfile
from ._limits import ConfigurationResult, LimitsCommand, limits_command


class ConfigurationCatalog(Protocol):
    def read(self) -> JsonObject: ...


class ConfigurationCommands(Protocol):
    def change(self, command: LimitsCommand, maximum: LimitsProfile) -> ConfigurationResult: ...


class WorkspaceService:
    def __init__(
        self, catalog: ConfigurationCatalog, commands: ConfigurationCommands, maximum: LimitsProfile
    ) -> None:
        self._catalog, self._commands, self._maximum = catalog, commands, maximum

    def catalog(self) -> JsonObject:
        return self._catalog.read()

    def change_limits(self, value: JsonObject) -> JsonObject:
        return self._commands.change(limits_command(value), self._maximum).to_value()
