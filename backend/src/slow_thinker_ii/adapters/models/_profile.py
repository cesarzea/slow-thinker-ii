"""Reviewed provider identities select explicit request and billing policies."""

from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.accounting import TariffRevision
from slow_thinker_ii.adapters.openai import OpenAIProfile
from slow_thinker_ii.contracts import JsonObject

from ._request import deepseek_request

PROFILES = {
    "openai": ("gpt-6-luna", "openai.gpt-6-luna.standard.text.v1"),
    "deepseek": ("deepseek-flash", "deepseek.flash.direct.v1"),
}
REASONING = {"openai": ("none",), "deepseek": ("none", "low", "high", "max")}


@dataclass(frozen=True)
class ModelProfile:
    revision: TariffRevision
    provider: Literal["openai", "deepseek"]
    model_alias: str
    default_output_tokens: int
    maximum_output_tokens: int
    returned_models: tuple[str, ...]

    def __post_init__(self) -> None:
        if (
            self.provider not in PROFILES
            or (self.revision.tariff.model, self.revision.tariff.profile) != PROFILES[self.provider]
        ):
            raise ValueError("Model and tariff must match the reviewed provider profile")
        self.openai_profile()

    def openai_profile(self) -> OpenAIProfile:
        return OpenAIProfile(
            self.revision,
            self.model_alias,
            self.default_output_tokens,
            self.maximum_output_tokens,
            self.returned_models,
        )

    def request(self, arguments_json: str) -> JsonObject:
        if self.provider == "openai":
            return self.openai_profile().request(arguments_json)
        return deepseek_request(
            arguments_json, self.model_alias, self.default_output_tokens, self.maximum_output_tokens
        )
