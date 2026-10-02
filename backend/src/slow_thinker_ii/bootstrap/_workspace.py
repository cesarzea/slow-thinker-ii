"""Compose product discovery, settings and independent reviewed tariff refreshes."""

from pathlib import Path

from slow_thinker_ii.adapters.preparation import ResourceSettings
from slow_thinker_ii.adapters.sqlite import (
    SqliteConfigurationCommands,
    SqliteDatabase,
    SqliteModelTariffReader,
    SqliteModelTariffStore,
    SqliteOperatorStore,
)
from slow_thinker_ii.adapters.tariffs import DeepSeekTariffSource
from slow_thinker_ii.adapters.workspace import WorkspaceCatalog
from slow_thinker_ii.application import (
    ExecutionConfiguration,
    TariffRefresh,
    TariffSource,
    workspace,
)


def workspace_service(
    database: SqliteDatabase,
    root: Path,
    commands: SqliteOperatorStore,
    configuration: ExecutionConfiguration,
    descriptors: tuple[str, ...],
) -> workspace.WorkspaceService:
    catalog = WorkspaceCatalog(
        root / "docs/contracts/schemas",
        root / "docs/contracts/examples",
        descriptors,
        commands.profile,
        configuration.limits,
        SqliteModelTariffReader(database),
    )
    return workspace.WorkspaceService(
        catalog, SqliteConfigurationCommands(database), configuration.limits
    )


def model_refreshes(
    database: SqliteDatabase,
    configuration: ExecutionConfiguration | None,
    sources: dict[str, TariffSource] | None,
) -> tuple[TariffRefresh, ...]:
    if configuration is None:
        return ()
    settings = ResourceSettings.model_validate_json(configuration.resources_json)
    if not any(profile.provider == "deepseek" for profile in settings.providers.values()):
        return ()
    profile_id = "deepseek.flash.direct.v1"
    source = (sources or {}).get(profile_id)
    return (
        TariffRefresh(
            source or DeepSeekTariffSource(), SqliteModelTariffStore(database, profile_id)
        ),
    )
