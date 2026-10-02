"""Public injected ports; workspace services do not construct concrete adapters."""

from typing import Protocol

from ._records import ModelTariffSelection


class ModelTariffReader(Protocol):
    def selected(self, profile_id: str) -> ModelTariffSelection | None: ...
