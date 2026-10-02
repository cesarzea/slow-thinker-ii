"""Public configuration-workspace contracts."""

from ._errors import WorkspaceError
from ._limits import (
    ConfigurationResult,
    LimitsCommand,
    apply_limits,
    limits_command,
    limits_value,
    within_limits,
)
from ._patch import patch_definition
from ._ports import ModelTariffReader
from ._records import ModelTariffSelection
from ._service import ConfigurationCatalog, ConfigurationCommands, WorkspaceService

__all__ = [
    "ModelTariffReader",
    "ModelTariffSelection",
    "WorkspaceError",
    "ConfigurationResult",
    "LimitsCommand",
    "apply_limits",
    "limits_command",
    "limits_value",
    "patch_definition",
    "ConfigurationCatalog",
    "ConfigurationCommands",
    "WorkspaceService",
    "within_limits",
]
