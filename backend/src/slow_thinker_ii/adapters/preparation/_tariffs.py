"""Freeze one validated price revision and preserve its latest successful source validation time."""

from dataclasses import dataclass

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.application import PreparationRejected, TariffStore

from ._models import ProviderProfile


@dataclass(frozen=True)
class SelectedTariff:
    revision: TariffRevision
    validated_at: int


def select_tariff(store: TariffStore) -> SelectedTariff | None:
    status = store.status()
    if status.revision is None or status.last_success is None:
        return None
    return SelectedTariff(store.revision(status.revision), status.last_success)


def admission_deadline(
    profile: ProviderProfile, selected: SelectedTariff | None, now: float, run_seconds: float
) -> float:
    if selected is None:
        raise PreparationRejected("tariff_unavailable")
    if selected.revision.tariff.model != profile.model:
        raise PreparationRejected("tariff_model_mismatch")
    if now < selected.validated_at:
        raise PreparationRejected("tariff_clock_regressed")
    deadline = min(
        profile.review_expires_at - run_seconds,
        selected.validated_at + profile.maximum_tariff_age_seconds,
    )
    if now >= deadline:
        raise PreparationRejected("pricing_review_expired")
    return deadline
