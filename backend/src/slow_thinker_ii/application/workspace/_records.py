"""Immutable model-tariff selections exposed to preparation and workspace discovery."""

from dataclasses import dataclass

from slow_thinker_ii.accounting import TariffRevision


@dataclass(frozen=True)
class ModelTariffSelection:
    revision: TariffRevision
    validated_at: int
