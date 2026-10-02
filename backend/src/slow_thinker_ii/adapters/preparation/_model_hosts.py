"""Bind a reviewed provider-neutral resource to one frozen tariff and launch-only credential."""

from slow_thinker_ii.adapters.models import ModelPricePolicy, ModelProfile
from slow_thinker_ii.adapters.process import HostBinding, ProcessSecret
from slow_thinker_ii.application import PreparationRejected, workspace
from slow_thinker_ii.contracts import JsonObject, encode_json

from ._host_profiles import HostProfile, HostRequest
from ._models import ModelReference, ProviderProfile, ResourceSettings
from ._tariffs import admission_deadline

REASONING = {"openai": ("none",), "deepseek": ("none", "low", "high", "max")}


class ModelResourceAdapter:
    def configure(self, request: HostRequest) -> HostProfile:
        reference = ModelReference.model_validate(request.component.config)
        provider = request.settings.providers.get(reference.provider_profile)
        if provider is None:
            raise PreparationRejected("provider_profile_unavailable")
        deadline = admission_deadline(
            provider, request.tariff, request.now, request.limits.run_seconds
        )
        assert request.tariff is not None
        if request.tariff.revision.tariff.profile != provider.billing_profile:
            raise PreparationRejected("tariff_billing_profile_mismatch")
        price = model_price(request, reference, provider)
        secret = ProcessSecret(
            "SLOW_THINKER_SECRET_MODEL", request.secrets.resolve(provider.credential_ref)
        )
        binding = HostBinding(
            provider_clients(request, provider.provider), (("complete", price),), (secret,)
        )
        selected = workspace.ModelTariffSelection(
            request.tariff.revision, request.tariff.validated_at
        )
        return HostProfile(
            binding,
            native_config(reference, provider),
            admit_before=deadline,
            model_tariff=selected,
        )


def native_config(reference: ModelReference, profile: ProviderProfile) -> str:
    return encode_json(
        {
            "provider": profile.provider,
            "model": profile.model,
            "model_alias": reference.model,
            "default_output_tokens": profile.default_output_tokens,
            "maximum_output_tokens": profile.maximum_output_tokens,
            "reasoning_efforts": list(REASONING[profile.provider]),
        }
    )


def provider_clients(request: HostRequest, provider: str) -> str:
    endpoint = (
        request.endpoints.provider if provider == "openai" else request.endpoints.deepseek_provider
    )
    return encode_json(
        {
            "provider": {
                "base_url": endpoint,
                "timeout_seconds": request.limits.call_seconds,
                "close_seconds": request.limits.shutdown_seconds,
                "max_response_bytes": request.limits.max_payload_bytes,
            }
        }
    )


def model_capabilities(settings: ResourceSettings) -> tuple[JsonObject, ...]:
    return tuple(
        {
            "provider_profile": identity,
            "provider": profile.provider,
            "model": profile.model,
            "reasoning_efforts": list(REASONING[profile.provider]),
            "supports_temperature": profile.provider == "deepseek",
            "default_output_tokens": profile.default_output_tokens,
            "maximum_output_tokens": profile.maximum_output_tokens,
            "billing_profile": profile.billing_profile,
            "review_expires_at": profile.review_expires_at,
        }
        for identity, profile in sorted(settings.providers.items())
    )


def model_price(
    request: HostRequest, reference: ModelReference, provider: ProviderProfile
) -> ModelPricePolicy:
    assert request.tariff is not None
    price = ModelPricePolicy(
        ModelProfile(
            request.tariff.revision,
            provider.provider,
            reference.model,
            provider.default_output_tokens,
            provider.maximum_output_tokens,
            provider.returned_models,
        )
    )
    return price
