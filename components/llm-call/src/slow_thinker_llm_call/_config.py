"""The LLM Call configuration, checked against the packaged declaration at startup."""

from dataclasses import dataclass

from slow_thinker_host import (
    JsonObject,
    JsonValue,
    check_schema,
    json_object,
    read_declaration,
    validate_value,
)


@dataclass(frozen=True)
class LLMCallConfig:
    """A valid configuration; `output_schema` is set exactly when the output is JSON."""

    prompt: str
    llm: str
    parameters: JsonObject
    input_format: JsonObject | None
    output_schema: JsonObject | None


def parse_config(config: JsonObject) -> LLMCallConfig:
    """Raise ValueError unless `config` is a complete, runnable LLM Call configuration."""
    declared = read_declaration("slow_thinker_llm_call")["config_schema"]
    try:
        validate_value(config, json_object(declared))
    except ValueError as error:
        raise ValueError(f"The LLM Call configuration is invalid: {error}") from error
    model = config["model"]
    if not isinstance(model, dict):
        raise ValueError("No LLM is selected")
    llm, parameters = model.get("llm"), model.get("parameters", {})
    if not isinstance(llm, str) or not llm or not isinstance(parameters, dict):
        raise ValueError("The LLM selection must name a catalog entry and its parameters")
    output = json_object(config["output_format"])
    return LLMCallConfig(
        prompt=str(config["prompt"]),
        llm=llm,
        parameters=json_object(parameters),
        input_format=_schema(config["input_format"]),
        output_schema=_schema(output["schema"]) if output["type"] == "json" else None,
    )


def _schema(value: JsonValue) -> JsonObject | None:
    if value is None:
        return None
    schema = json_object(value)
    check_schema(schema)
    return schema
