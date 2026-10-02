"""Immutable reviewed native provider identities and output bounds."""

from dataclasses import dataclass
from typing import Literal

from slow_thinker_host import JsonObject

type Provider = Literal["openai", "deepseek"]
REASONING = {"openai": ("none",), "deepseek": ("none", "low", "high", "max")}


@dataclass(frozen=True)
class ModelProviderConfig:
    provider: Provider
    model: str
    model_alias: str
    default_output_tokens: int
    maximum_output_tokens: int
    reasoning_efforts: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.provider not in REASONING or not self.model or not self.model_alias:
            raise ValueError("A reviewed provider and model identity are required")
        if self.reasoning_efforts != REASONING[self.provider]:
            raise ValueError("Unsupported reviewed reasoning capabilities")
        if (
            any(
                type(value) is not int
                for value in (self.default_output_tokens, self.maximum_output_tokens)
            )
            or not 1 <= self.default_output_tokens <= self.maximum_output_tokens
        ):
            raise ValueError("Invalid configured output limits")
        expected = "gpt-6-luna" if self.provider == "openai" else "deepseek-flash"
        if self.model != expected:
            raise ValueError("Unsupported native model profile")


def parse_config(record: JsonObject) -> ModelProviderConfig:
    fields = {
        "provider",
        "model",
        "model_alias",
        "default_output_tokens",
        "maximum_output_tokens",
        "reasoning_efforts",
    }
    if set(record) != fields:
        raise ValueError("Unsupported model-provider configuration")
    provider, model, alias = record["provider"], record["model"], record["model_alias"]
    if (
        provider not in ("openai", "deepseek")
        or not isinstance(model, str)
        or not isinstance(alias, str)
    ):
        raise ValueError("Invalid provider or model identity")
    default, maximum = record["default_output_tokens"], record["maximum_output_tokens"]
    efforts = record["reasoning_efforts"]
    if type(default) is not int or type(maximum) is not int or not isinstance(efforts, list):
        raise ValueError("Invalid output limits or reasoning capabilities")
    if any(not isinstance(item, str) for item in efforts):
        raise ValueError("Invalid reasoning capability")
    selected: Provider = "openai" if provider == "openai" else "deepseek"
    return ModelProviderConfig(
        selected, model, alias, default, maximum, tuple(str(v) for v in efforts)
    )
