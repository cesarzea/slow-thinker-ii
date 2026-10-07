"""LLM catalog entries and the parameter schemas generated from reviewed model settings."""

from dataclasses import dataclass
from typing import Literal

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object

from ._parameters import defaults_added, parameter_sentences


@dataclass(frozen=True)
class LlmModelSettings:
    id: str
    label: str
    provider: str
    model: str
    max_output_tokens: int
    default_output_tokens: int
    reasoning_efforts: tuple[str, ...]
    temperature: Literal["unsupported", "supported", "without_reasoning"]


@dataclass(frozen=True)
class LlmEntry:
    id: str
    label: str
    provider: str
    parameters: JsonObject

    def document(self) -> JsonObject:
        parameters = json_object(self.parameters)
        return {
            "id": self.id,
            "label": self.label,
            "provider": self.provider,
            "parameters": parameters,
        }

    def parameter_problems(self, parameters: JsonObject) -> tuple[str, ...]:
        """Sorted distinct sentences for each way `parameters` violates `self.parameters`."""
        return parameter_sentences(self.parameters, parameters)

    def with_defaults(self, parameters: JsonObject) -> JsonObject:
        """A copy with the schema defaults of missing top-level properties that keep it valid."""
        return defaults_added(self.parameters, parameters)


def llm_entry(settings: LlmModelSettings) -> LlmEntry:
    if not 1 <= settings.default_output_tokens <= settings.max_output_tokens:
        raise ValueError(
            f"{settings.id}: default_output_tokens must be from 1 to max_output_tokens"
        )
    return LlmEntry(settings.id, settings.label, settings.provider, _parameters(settings))


def _parameters(settings: LlmModelSettings) -> JsonObject:
    """The closed parameter schema of the LLM service contract, in its documented order."""
    properties: JsonObject = {}
    if len(settings.reasoning_efforts) > 1:
        properties["reasoning_effort"] = _reasoning(settings.reasoning_efforts)
    if settings.temperature != "unsupported":
        properties["temperature"] = _temperature()
    properties["max_completion_tokens"] = _output_tokens(settings)
    schema: JsonObject = {
        "type": "object",
        "additionalProperties": False,
        "required": ["max_completion_tokens"],
        "properties": properties,
    }
    if settings.temperature == "without_reasoning":
        schema["if"] = {"properties": {"reasoning_effort": {"const": "none"}}}
        schema["else"] = {"properties": {"temperature": False}}
    return schema


def _reasoning(efforts: tuple[str, ...]) -> JsonObject:
    choices: list[JsonValue] = [*efforts]
    return {"title": "Reasoning", "enum": choices, "default": efforts[0]}


def _temperature() -> JsonObject:
    return {"type": "number", "title": "Temperature", "minimum": 0, "maximum": 2, "default": 1}


def _output_tokens(settings: LlmModelSettings) -> JsonObject:
    return {
        "type": "integer",
        "title": "Max output tokens",
        "minimum": 1,
        "maximum": settings.max_output_tokens,
        "default": settings.default_output_tokens,
    }
