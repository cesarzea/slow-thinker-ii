"""Freeze one validated price revision and preserve its latest successful source validation time."""

from dataclasses import dataclass

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.adapters.catalog import ComponentRecord
from slow_thinker_ii.application import PreparationRejected, TariffStore, workspace

from ._models import ModelReference, ProviderProfile, ResourceSettings


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


def model_tariff(
    component: ComponentRecord,
    settings: ResourceSettings,
    legacy: SelectedTariff | None,
    reader: workspace.ModelTariffReader | None,
) -> SelectedTariff | None:
    if component.type_id != "model-provider":
        return legacy
    reference = ModelReference.model_validate(component.config)
    profile = settings.providers.get(reference.provider_profile)
    if profile is None:
        raise PreparationRejected("provider_profile_unavailable")
    if reader is None:
        if (
            profile.provider == "openai"
            and legacy is not None
            and legacy.revision.tariff.profile == profile.billing_profile
        ):
            return legacy
        return None
    selected = reader.selected(profile.billing_profile)
    return None if selected is None else SelectedTariff(selected.revision, selected.validated_at)
