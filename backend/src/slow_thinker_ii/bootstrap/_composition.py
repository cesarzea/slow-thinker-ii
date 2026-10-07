"""The composition root: catalog, providers, launch targets, use cases and the HTTP app."""

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI

from slow_thinker_ii.adapters.hosts import LaunchTarget
from slow_thinker_ii.adapters.http import HttpSettings, create_http_app
from slow_thinker_ii.adapters.installations import InstallationCatalog, InstalledComponents
from slow_thinker_ii.adapters.sqlite import SqliteDatabase
from slow_thinker_ii.application import LlmProvider
from slow_thinker_ii.catalog import Catalog, ComponentDeclaration, llm_entry, platform_declarations

from ._configuration import ServerConfiguration, load_configuration
from ._document import invalid
from ._lifespan import lifespan
from ._providers import configured_provider
from ._secrets import EnvironmentSecrets
from ._server import ServerSection
from ._services import use_cases

CONFIGURATION = "SLOW_THINKER_CONFIGURATION"


@dataclass(frozen=True)
class AppOverrides:
    """For tests and browser journeys only.

    With `provider`, no provider credential is read; with both `components` and
    `launch_targets`, no installation is verified.
    """

    components: Sequence[ComponentDeclaration] | None = None  # replaces installed declarations
    launch_targets: LaunchTarget | None = None  # replaces installed environments
    provider: LlmProvider | None = None  # replaces the configured providers


def configured_app() -> FastAPI:
    """The uvicorn factory: the configuration file named by `SLOW_THINKER_CONFIGURATION`.

    A configuration, secret or installation problem ends the process with its message
    instead of a traceback.
    """
    try:
        path = os.environ.get(CONFIGURATION, "")
        if not path:
            raise ValueError(f"The environment variable {CONFIGURATION} must name the file.")
        return create_app(load_configuration(Path(path)), os.environ)
    except (OSError, RuntimeError, ValueError) as error:
        raise SystemExit(f"Slow Thinker II cannot start: {error}") from None


def create_app(
    configuration: ServerConfiguration,
    environment: Mapping[str, str],
    overrides: AppOverrides | None = None,
) -> FastAPI:
    """Composes the application; the database is opened only when its lifespan starts."""
    chosen = overrides or AppOverrides()
    secrets = EnvironmentSecrets(environment)
    server = configuration.server
    token = None if server.operator_authentication == "none" else secrets.operator_token()
    settings = _http_settings(server, token)
    provider = chosen.provider
    if provider is None:
        provider = configured_provider(configuration, secrets)
    declarations, targets = _components(configuration, chosen)
    entries = [llm_entry(model.settings) for model in configuration.models]
    catalog = Catalog([*platform_declarations(), *declarations], entries)
    database = SqliteDatabase(configuration.database)
    services = use_cases(configuration, database, lambda: catalog, provider, targets)
    return create_http_app(
        services, settings, lifespan(database, services.runs, configuration.workspace)
    )


def _http_settings(server: ServerSection, token: str | None) -> HttpSettings:
    """The operator guard (`None`: no operator authentication) and the compiled interface."""
    static = server.static_directory
    if static is not None and not static.is_dir():
        raise ValueError(
            f"The interface directory {static} does not exist. Build it with "
            '"npm run build", or set server.static_directory to null.'
        )
    hosts, origins = server.allowed_hosts, server.allowed_origins
    try:
        return HttpSettings(token, hosts, origins, static_directory=static)
    except ValueError as error:  # the token is already checked: a host or an origin is not
        raise invalid("/server", str(error).rstrip(".")) from None


def _components(
    configuration: ServerConfiguration, overrides: AppOverrides
) -> tuple[Sequence[ComponentDeclaration], LaunchTarget]:
    """The catalog's package declarations and their launch targets, verified when installed."""
    if overrides.components is not None and overrides.launch_targets is not None:
        return overrides.components, overrides.launch_targets
    section = configuration.components
    catalog = InstallationCatalog(section.installation_root, section.uv, section.python)
    installed = InstalledComponents(catalog, section.resolutions)
    found = [component.declaration for component in installed.components()]
    declarations = found if overrides.components is None else overrides.components
    targets = installed if overrides.launch_targets is None else overrides.launch_targets
    return declarations, targets
