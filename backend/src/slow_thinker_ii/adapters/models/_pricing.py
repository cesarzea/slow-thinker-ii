"""Reserve peak capacity and settle only verified direct usage in a single billing interval."""

from slow_thinker_ii.accounting import account_fraction
from slow_thinker_ii.adapters.openai import OpenAIPricePolicy
from slow_thinker_ii.application import ChargeBasis, ChargeEvidence
from slow_thinker_ii.contracts import (
    JsonObject,
    OperationResult,
    decode_json,
    encode_json,
    json_object,
)

from ._billing import direct_billing
from ._profile import ModelProfile
from ._timing import interval_rates
from ._usage import direct_usage


class ModelPricePolicy:
    def __init__(self, profile: ModelProfile) -> None:
        self._profile = profile
        self._legacy = (
            OpenAIPricePolicy(profile.openai_profile()) if profile.provider == "openai" else None
        )
        self._billing = direct_billing(profile.revision) if profile.provider == "deepseek" else None

    def quote(self, arguments_json: str) -> ChargeBasis:
        if self._legacy is not None:
            return self._legacy.quote(arguments_json)
        request = self._profile.request(arguments_json)
        cap = request["max_tokens"]
        assert type(cap) is int
        tariff = self._profile.revision.tariff
        source = json_object(decode_json(self._profile.revision.source_json))
        basis: JsonObject = {
            "bound_policy": "published-peak-capacity-v1",
            "provider": "deepseek",
            "requested_model": self._profile.model_alias,
            "model": tariff.model,
            "input_capacity": tariff.input_capacity,
            "max_tokens": cap,
            "native_request_options": {k: v for k, v in request.items() if k != "messages"},
            "billing": source["normalized"],
        }
        return ChargeBasis(
            tariff.reservation(cap), self._profile.revision.digest, encode_json(basis)
        )

    def reconcile(self, result: OperationResult) -> ChargeEvidence:
        if self._legacy is not None:
            return self._legacy.reconcile(result)
        payload = json_object(decode_json(result.payload_json))
        response = payload.get("response")
        if result.is_error or not isinstance(response, dict):
            return ChargeEvidence(None, None, "deepseek.usage")
        evidence: JsonObject = {
            "reported_usage": response.get("usage"),
            "transport": payload.get("transport"),
            "created": response.get("created"),
            "source_revision": self._profile.revision.digest,
        }
        try:
            amount = self._amount(payload, response)
        except (ValueError, OverflowError, KeyError) as error:
            evidence.update(status="unavailable", reason=unavailable_reason(error))
            return ChargeEvidence(encode_json(evidence), None, "deepseek.usage")
        evidence.update(
            status="verified", billing_assumptions="reviewed_direct_schedule_and_calendar"
        )
        return ChargeEvidence(encode_json(evidence), amount, "deepseek.usage")

    def _amount(self, payload: JsonObject, response: JsonObject) -> int:
        assert self._billing is not None
        usage = direct_usage(response, self._profile.returned_models)
        tariff = self._profile.revision.tariff
        if usage.prompt > tariff.input_capacity or usage.completion > tariff.output_capacity:
            raise ValueError("usage_exceeds_reviewed_capacity")
        rates = interval_rates(payload, response, self._billing)
        return account_fraction(
            (usage.prompt - usage.cached) * rates.input
            + usage.cached * rates.cached
            + usage.completion * rates.output
        )


def unavailable_reason(error: Exception) -> str:
    supported = {
        "unverified_transport_timing",
        "unreviewed_billing_interval",
        "billing_interval_boundary",
        "inconsistent_provider_timing",
        "billing_identity_mismatch",
        "incomplete_usage",
        "inconsistent_usage",
        "usage_exceeds_reviewed_capacity",
    }
    reason = str(error)
    return reason if reason in supported else "unverified_usage_or_billing_interval"
