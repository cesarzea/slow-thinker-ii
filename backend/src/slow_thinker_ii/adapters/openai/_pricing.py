"""Quote and settle against one frozen tariff revision, preserving unknown obligations."""

from slow_thinker_ii.accounting import TokenRates, account_fraction
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence
from slow_thinker_ii.contracts import (
    JsonObject,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)

from ._profile import OpenAIProfile
from ._usage import reported_usage


class OpenAIPricePolicy:
    def __init__(self, profile: OpenAIProfile) -> None:
        self._profile = profile

    def quote(self, arguments_json: str) -> ChargeBasis:
        request = self._profile.request(arguments_json)
        cap = request["max_completion_tokens"]
        assert type(cap) is int
        revision = self._profile.revision
        tariff = revision.tariff
        basis: JsonObject = {
            "bound_policy": "published-capacity-v1",
            "profile": tariff.profile,
            "requested_model": self._profile.model_alias,
            "model": tariff.model,
            "input_capacity": tariff.input_capacity,
            "output_capacity": tariff.output_capacity,
            "long_context_start": tariff.long_context_start,
            "max_completion_tokens": cap,
            "service_tier": "default",
            "short_rates": rates(tariff.short),
            "long_rates": rates(tariff.long),
        }
        return ChargeBasis(tariff.reservation(cap), revision.digest, encode_json(basis))

    def reconcile(self, result: OperationResult) -> ChargeEvidence:
        payload = json_object(decode_json(result.payload_json))
        response = payload.get("response")
        if result.is_error or not isinstance(response, dict):
            return ChargeEvidence(None, None, "openai.usage")
        evidence: JsonObject = {"reported_usage": response.get("usage")}
        try:
            usage = reported_usage(response, self._profile.returned_models)
            amount = account_fraction(self._profile.revision.tariff.charge(usage))
        except ValueError:
            evidence.update(
                {"status": "unavailable", "reason": "unverified_usage_or_billing_profile"}
            )
            return ChargeEvidence(encode_json(evidence), None, "openai.usage")
        evidence["status"] = "verified"
        return ChargeEvidence(encode_json(evidence), amount, "openai.usage")


def rates(value: TokenRates) -> JsonObject:
    return {
        "input": str(value.input),
        "cached": str(value.cached),
        "cache_write": str(value.cache_write),
        "output": str(value.output),
    }
