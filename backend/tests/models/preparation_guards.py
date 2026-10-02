"""Public host requests and tariff reader substitutions exercise preparation failure boundaries."""

from dataclasses import dataclass

from slow_thinker_ii.adapters.preparation import HostProfile, HostRequest, ModelResourceAdapter
from slow_thinker_ii.application import workspace


class RecordingModelAdapter:
    def __init__(self) -> None:
        self.requests: list[HostRequest] = []

    def configure(self, request: HostRequest) -> HostProfile:
        self.requests.append(request)
        return ModelResourceAdapter().configure(request)


@dataclass(frozen=True)
class FrozenReader:
    selection: workspace.ModelTariffSelection

    def selected(self, profile_id: str) -> workspace.ModelTariffSelection:
        assert profile_id == "deepseek.flash.direct.v1"
        return self.selection
