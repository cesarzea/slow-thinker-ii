"""Browser discovery/settings use production adapters and trusted synthetic resources."""

from pathlib import Path

from slow_thinker_ii.adapters.sqlite import (
    SqliteConfigurationCommands,
    SqliteDatabase,
    SqliteModelTariffReader,
    SqliteOperatorStore,
)
from slow_thinker_ii.adapters.workspace import WorkspaceCatalog
from slow_thinker_ii.application import ExecutionConfiguration, workspace

from .workspace_data import workspace_descriptors


def browser_workspace(
    database: SqliteDatabase,
    root: Path,
    commands: SqliteOperatorStore,
    configuration: ExecutionConfiguration,
) -> workspace.WorkspaceService:
    catalog = WorkspaceCatalog(
        root / "docs/contracts/schemas",
        root / "docs/contracts/examples",
        workspace_descriptors(root),
        commands.profile,
        configuration.limits,
        SqliteModelTariffReader(database),
    )
    return workspace.WorkspaceService(
        catalog, SqliteConfigurationCommands(database), configuration.limits
    )
