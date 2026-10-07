"""The use cases over the SQLite stores, sharing one clock with the grants they issue."""

from collections.abc import Callable

from slow_thinker_ii.access import Grants
from slow_thinker_ii.adapters.hosts import HostSettings, LaunchTarget, LocalHostLauncher
from slow_thinker_ii.adapters.http import HttpServices
from slow_thinker_ii.adapters.sqlite import (
    SqliteDatabase,
    SqliteGraphStore,
    SqliteLedger,
    SqliteRunStore,
)
from slow_thinker_ii.application import (
    GraphLibrary,
    LlmGateway,
    LlmProvider,
    ReportService,
    RunService,
    UsageService,
)
from slow_thinker_ii.catalog import Catalog

from ._configuration import ServerConfiguration
from ._lifespan import SystemClock


def use_cases(
    configuration: ServerConfiguration,
    database: SqliteDatabase,
    catalog: Callable[[], Catalog],
    provider: LlmProvider,
    targets: LaunchTarget,
) -> HttpServices:
    """Every use case the HTTP adapter serves, over one database and one clock."""
    clock, budgets = SystemClock(), configuration.budgets
    graphs, ledger = SqliteGraphStore(database), SqliteLedger(database)
    runs = RunService(
        graphs=graphs,
        runs=SqliteRunStore(database),
        ledger=ledger,
        launcher=host_launcher(configuration, targets),
        grants=Grants(clock.monotonic),
        clock=clock,
        catalog=catalog,
        budgets=budgets,
        settings=configuration.runtime.runs,
    )
    models = configuration.models
    gateway = LlmGateway(
        runs=runs, ledger=ledger, provider=provider, models=models, budgets=budgets, clock=clock
    )
    library, usage = GraphLibrary(graphs, catalog, clock), UsageService(ledger, budgets, clock)
    return HttpServices(catalog, library, runs, gateway, ReportService(runs), usage)


def host_launcher(configuration: ServerConfiguration, targets: LaunchTarget) -> LocalHostLauncher:
    """Hosts call the platform back on the public URL: `/v1` for models, `/mcp` for reports."""
    url = configuration.server.public_url
    startup = configuration.runtime.host_startup_seconds
    settings = HostSettings(
        configuration.workspace, f"{url}/v1", f"{url}/mcp", startup_seconds=startup
    )
    return LocalHostLauncher(targets, settings)
