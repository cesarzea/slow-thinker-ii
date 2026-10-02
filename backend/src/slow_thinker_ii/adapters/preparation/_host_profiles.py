"""Host adapters are registered backend extensions selected by a trusted configuration."""

from dataclasses import dataclass, field
from typing import Protocol

from slow_thinker_ii.adapters.catalog import ComponentRecord, GraphRecord
from slow_thinker_ii.adapters.process import HostBinding
from slow_thinker_ii.application import LimitsProfile, ModelBinding, workspace

from ._endpoints import ServiceEndpoints
from ._models import ResourceSettings
from ._secrets import SecretSource
from ._tariffs import SelectedTariff


@dataclass(frozen=True)
class HostRequest:
    instance_id: str
    component: ComponentRecord
    graph: GraphRecord
    settings: ResourceSettings
    limits: LimitsProfile
    endpoints: ServiceEndpoints
    tariff: SelectedTariff | None
    now: float
    secrets: SecretSource = field(repr=False)
    runtime_id: str = ""


@dataclass(frozen=True)
class HostProfile:
    binding: HostBinding
    config_json: str | None = None
    models: tuple[ModelBinding, ...] = ()
    admit_before: float | None = None
    model_tariff: workspace.ModelTariffSelection | None = None


class HostAdapter(Protocol):
    def configure(self, request: HostRequest) -> HostProfile: ...


class PlainHostAdapter:
    def configure(self, request: HostRequest) -> HostProfile:
        del request
        return HostProfile(HostBinding())
