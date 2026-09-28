"""The admitted model identity and token bounds stay fixed for a host lifetime."""

from dataclasses import dataclass

from slow_thinker_host import JsonObject


@dataclass(frozen=True)
class ModelConfig:
    model_alias: str
    model: str
    default_output_tokens: int
    maximum_output_tokens: int

    def __post_init__(self) -> None:
        if not self.model_alias or not self.model:
            raise ValueError("Model identities are required")
        if (
            any(
                type(value) is not int
                for value in (self.default_output_tokens, self.maximum_output_tokens)
            )
            or not 1 <= self.default_output_tokens <= self.maximum_output_tokens
        ):
            raise ValueError("Invalid configured output limits")


def parse_config(record: JsonObject) -> ModelConfig:
    if set(record) != {"model_alias", "model", "default_output_tokens", "maximum_output_tokens"}:
        raise ValueError("Unsupported model configuration")
    alias, model = record["model_alias"], record["model"]
    default, maximum = record["default_output_tokens"], record["maximum_output_tokens"]
    if not isinstance(alias, str) or not isinstance(model, str):
        raise ValueError("Invalid model identity")
    if type(default) is not int or type(maximum) is not int:
        raise ValueError("Invalid model token limits")
    return ModelConfig(alias, model, default, maximum)
