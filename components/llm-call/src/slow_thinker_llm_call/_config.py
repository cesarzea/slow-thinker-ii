"""Freeze validated configuration without retaining caller-owned mutable objects."""

from dataclasses import dataclass
from typing import Literal

from openai.types.chat.completion_create_params import CompletionCreateParamsNonStreaming
from slow_thinker_host import JsonObject, check_schema, encode_json, json_object

from ._types import JsonOutput, LLMCallConfig, TextOutput

RESERVED = {
    "model",
    "messages",
    "stream",
    "response_format",
    "n",
    "base_url",
    "api_key",
    "timeout",
    "max_retries",
    "extra_body",
    "extra_headers",
    "extra_query",
}


@dataclass(frozen=True)
class FrozenConfig:
    instructions: str
    input_schema: str
    parameters: str
    format: Literal["text", "json"]
    output_schema: str | None


def _output(record: JsonObject) -> TextOutput | JsonOutput:
    if record == {"format": "text"}:
        return TextOutput(format="text")
    if set(record) != {"format", "schema"} or record["format"] != "json":
        raise ValueError("Unsupported output configuration")
    schema = json_object(record["schema"])
    check_schema(schema)
    return JsonOutput(format="json", schema=schema)


def parse_config(value: object) -> LLMCallConfig:
    record = json_object(value)
    if set(record) != {"instructions", "input_schema", "parameters", "output"}:
        raise ValueError("Unsupported LLMCall configuration fields")
    instructions = record["instructions"]
    if not isinstance(instructions, str) or not instructions:
        raise ValueError("Instructions must be a non-empty string")
    schema = json_object(record["input_schema"])
    if schema.get("type") != "object":
        raise ValueError("LLMCall input must have an object schema")
    check_schema(schema)
    parameters = json_object(record["parameters"])
    allowed = set(CompletionCreateParamsNonStreaming.__annotations__) - RESERVED
    if set(parameters) - allowed:
        raise ValueError("Unsupported or reserved generation parameters")
    return LLMCallConfig(
        instructions=instructions,
        input_schema=schema,
        parameters=parameters,
        output=_output(json_object(record["output"])),
    )


def freeze(config: LLMCallConfig) -> FrozenConfig:
    isolated = parse_config(config)
    output = isolated["output"]
    return FrozenConfig(
        isolated["instructions"],
        encode_json(isolated["input_schema"]),
        encode_json(isolated["parameters"]),
        output["format"],
        encode_json(output["schema"]) if output["format"] == "json" else None,
    )
