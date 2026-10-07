"""The validated server configuration, with paths made absolute against the working directory."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

from slow_thinker_ii.accounting import parse_usd
from slow_thinker_ii.application import BudgetLimits, LlmModel, RunSettings

from ._document import (
    ConfigurationDocument,
    ProviderDocument,
    ProvidersDocument,
    invalid,
    read_document,
)
from ._models import SIMULATED, configured_models, scripted_replies
from ._server import ServerSection, server_section


@dataclass(frozen=True)
class ComponentsSection:
    installation_root: Path
    uv: Path
    python: Path
    resolutions: tuple[str, ...]  # installed resolution identities


@dataclass(frozen=True)
class ProviderSection:
    name: Literal["openai", "deepseek"]
    base_url: str
    credential_env: str  # the environment variable that holds the key
    timeout_seconds: float


@dataclass(frozen=True)
class RuntimeSection:
    runs: RunSettings  # max_active_runs, max_activation_seconds
    host_startup_seconds: float


@dataclass(frozen=True)
class ServerConfiguration:
    database: Path
    workspace: Path
    server: ServerSection
    components: ComponentsSection
    providers: tuple[ProviderSection, ...]  # the network providers; `simulated` needs none
    replies: Mapping[str, tuple[str, ...]]  # scripted replies of simulated models, by id
    models: tuple[LlmModel, ...]
    budgets: BudgetLimits
    runtime: RuntimeSection


def load_configuration(path: Path) -> ServerConfiguration:
    """Reads and checks the configuration; `ValueError` names each invalid location."""
    document = read_document(path)
    providers = _providers(document.llm.providers)
    names = {provider.name for provider in providers}
    if document.llm.providers.simulated is not None:
        names.add(SIMULATED)
    runtime = document.runtime
    return ServerConfiguration(
        _absolute(document.database),
        _absolute(document.workspace),
        server_section(document.server),
        _components(document),
        providers,
        scripted_replies(document.llm.models),
        configured_models(document.llm.models, names),
        _budgets(document),
        RuntimeSection(
            RunSettings(runtime.max_active_runs, runtime.max_activation_seconds),
            runtime.host_startup_seconds,
        ),
    )


def _providers(document: ProvidersDocument) -> tuple[ProviderSection, ...]:
    configured: tuple[tuple[Literal["openai", "deepseek"], ProviderDocument | None], ...] = (
        ("openai", document.openai),
        ("deepseek", document.deepseek),
    )
    return tuple(
        ProviderSection(name, section.base_url, section.credential_env, section.timeout_seconds)
        for name, section in configured
        if section is not None
    )


def _components(document: ConfigurationDocument) -> ComponentsSection:
    section = document.components
    return ComponentsSection(
        _absolute(section.installation_root),
        _absolute(section.uv),
        _absolute(section.python),
        section.resolutions,
    )


def _budgets(document: ConfigurationDocument) -> BudgetLimits:
    budgets = document.budgets
    amounts: list[int] = []
    for name, text in (("daily_usd", budgets.daily_usd), ("monthly_usd", budgets.monthly_usd)):
        try:
            amounts.append(parse_usd(text))
        except ValueError as error:
            raise invalid(f"/budgets/{name}", str(error)) from None
    return BudgetLimits(*amounts)


def _absolute(text: str) -> Path:
    """A configured path; a relative one is taken from the working directory."""
    return Path(text).absolute()
