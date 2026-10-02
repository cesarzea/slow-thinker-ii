"""Bind ordinary OpenAI clients and the metered resource to approved platform transports."""

from slow_thinker_ii.access import OperationAddress
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy, OpenAIProfile
from slow_thinker_ii.adapters.process import HostBinding, ProcessSecret
from slow_thinker_ii.application import ModelBinding, PreparationRejected, workspace
from slow_thinker_ii.contracts import encode_json

from ._host_profiles import HostProfile, HostRequest
from ._models import ModelReference, ProviderProfile
from ._tariffs import admission_deadline


class OpenAIClientAdapter:
    def configure(self, request: HostRequest) -> HostProfile:
        target = request.component.resources.get("model")
        if target is None or target not in request.graph.components:
            raise PreparationRejected("model_resource_required")
        model = ModelReference.model_validate(request.graph.components[target].config)
        clients = encode_json(
            {
                "openai": {
                    "base_url": request.endpoints.gateway,
                    "model": model.model,
                    "timeout_seconds": request.limits.call_seconds,
                    "close_seconds": request.limits.shutdown_seconds,
                }
            }
        )
        binding = ModelBinding(
            request.instance_id, model.model, OperationAddress(target, "complete")
        )
        return HostProfile(HostBinding(clients), models=(binding,))


class OpenAIResourceAdapter:
    def configure(self, request: HostRequest) -> HostProfile:
        reference = ModelReference.model_validate(request.component.config)
        provider = request.settings.providers.get(reference.provider_profile)
        if provider is None:
            raise PreparationRejected("provider_profile_unavailable")
        if provider.provider != "openai":
            raise PreparationRejected("legacy_provider_profile_mismatch")
        deadline = admission_deadline(
            provider, request.tariff, request.now, request.limits.run_seconds
        )
        assert request.tariff is not None
        price = OpenAIPricePolicy(
            OpenAIProfile(
                request.tariff.revision,
                reference.model,
                provider.default_output_tokens,
                provider.maximum_output_tokens,
                provider.returned_models,
            )
        )
        credential = ProcessSecret(
            "SLOW_THINKER_SECRET_OPENAI", request.secrets.resolve(provider.credential_ref)
        )
        binding = HostBinding(provider_clients(request), (("complete", price),), (credential,))
        selected = workspace.ModelTariffSelection(
            request.tariff.revision, request.tariff.validated_at
        )
        return HostProfile(
            binding, model_config(reference, provider), admit_before=deadline, model_tariff=selected
        )


def provider_clients(request: HostRequest) -> str:
    return encode_json(
        {
            "provider": {
                "base_url": request.endpoints.provider,
                "timeout_seconds": request.limits.call_seconds,
                "close_seconds": request.limits.shutdown_seconds,
                "max_response_bytes": request.limits.max_payload_bytes,
            }
        }
    )


def model_config(reference: ModelReference, provider: ProviderProfile) -> str:
    return encode_json(
        {
            "model_alias": reference.model,
            "model": provider.model,
            "default_output_tokens": provider.default_output_tokens,
            "maximum_output_tokens": provider.maximum_output_tokens,
        }
    )
