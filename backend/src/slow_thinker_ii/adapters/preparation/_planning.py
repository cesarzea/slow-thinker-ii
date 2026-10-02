"""Expand host settings before contract validation, without starting business hosts."""

from collections.abc import Mapping

from slow_thinker_ii.adapters.catalog import GraphRecord
from slow_thinker_ii.application import LimitsProfile, PreparationRejected, workspace

from ._endpoints import ServiceEndpoints
from ._host_profiles import HostAdapter, HostProfile, HostRequest
from ._models import ResourceSettings
from ._secrets import SecretSource
from ._tariffs import SelectedTariff, model_tariff


class HostPlanner:
    def __init__(
        self,
        adapters: Mapping[str, HostAdapter],
        endpoints: ServiceEndpoints,
        secrets: SecretSource,
        model_tariffs: workspace.ModelTariffReader | None = None,
    ) -> None:
        self._adapters, self._endpoints, self._secrets = adapters, endpoints, secrets
        self._model_tariffs = model_tariffs

    def configure(
        self,
        graph: GraphRecord,
        limits: LimitsProfile,
        settings: ResourceSettings,
        tariff: SelectedTariff | None,
        now: float,
        runtime_id: str = "",
    ) -> dict[str, HostProfile]:
        result: dict[str, HostProfile] = {}
        for identity, component in graph.components.items():
            adapter = self._adapter(component.type_id, component.type_version, settings)
            selected = model_tariff(component, settings, tariff, self._model_tariffs)
            request = HostRequest(
                identity,
                component,
                graph,
                settings,
                limits,
                self._endpoints,
                selected,
                now,
                self._secrets,
                runtime_id,
            )
            result[identity] = adapter.configure(request)
        return result

    def _adapter(self, type_id: str, version: str, settings: ResourceSettings) -> HostAdapter:
        names = [
            item.host_adapter
            for item in settings.installations
            if (item.type_id, item.type_version) == (type_id, version)
        ]
        adapter = None if len(names) != 1 else self._adapters.get(names[0])
        if adapter is None:
            raise PreparationRejected("host_adapter_unavailable")
        return adapter
