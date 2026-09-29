"""Local application composition."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from slow_thinker_ii.adapters.catalog import BundledDefinitionStore
from slow_thinker_ii.adapters.http import (
    OperatorBoundary,
    catalog_router,
    mcp_router,
    openai_router,
    operator_router,
    tariff_router,
)
from slow_thinker_ii.adapters.sqlite import SqliteDatabase, SqliteTariffStore
from slow_thinker_ii.adapters.tariffs import VercelTariffSource
from slow_thinker_ii.application import ExperimentCatalog, TariffRefresh, TariffSource

from ._configuration import configured_execution, load_execution_setup
from ._execution import ExecutionComposition, ExecutionServices, ExecutionSetup
from ._refresh import TariffLifetime

__all__ = [
    "create_app",
    "configured_app",
    "ExecutionSetup",
    "load_execution_setup",
    "ExecutionServices",
]


def create_app(
    database_path: Path | None = None,
    tariff_source: TariffSource | None = None,
    execution_setup: ExecutionComposition | None = None,
) -> FastAPI:
    root = Path(__file__).resolve().parents[4]
    catalog = ExperimentCatalog(BundledDefinitionStore(root / "docs/contracts/examples"))
    database = SqliteDatabase(database_path or root / ".local/state.sqlite3")
    tariffs = SqliteTariffStore(database)
    execution = None if execution_setup is None else execution_setup.build(database, root)
    lifetime = TariffLifetime(
        database, TariffRefresh(tariff_source or VercelTariffSource(), tariffs), execution
    )
    app = FastAPI(
        title="Slow Thinker II", docs_url=None, redoc_url=None, lifespan=lifetime.lifespan
    )
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
    app.include_router(catalog_router(catalog))
    app.include_router(tariff_router(tariffs))
    attach_execution(app, execution)
    return app


def attach_execution(app: FastAPI, execution: ExecutionServices | None) -> None:
    if execution is not None:
        app.add_middleware(OperatorBoundary, access=execution.access)
        bound = execution.configuration.limits.max_payload_bytes
        app.include_router(
            operator_router(
                execution.coordinator,
                execution.commands,
                execution.queries,
                execution.access,
                bound,
            )
        )
        app.include_router(openai_router(execution.coordinator.gateway, bound))
        app.include_router(mcp_router(execution.coordinator.components, bound))


def configured_app() -> FastAPI:
    return create_app(execution_setup=configured_execution())
