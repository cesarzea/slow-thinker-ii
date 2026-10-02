"""New browser fixtures use canonical descriptors and public component operation contracts."""

from pathlib import Path

from slow_thinker_ii.contracts import JsonObject
from slow_thinker_llm_call import LLMCall

ROOT = Path(__file__).resolve().parents[3]


def resource_descriptor_path(type_id: str) -> Path:
    if type_id == "example.resource-agent":
        return ROOT / "examples/resource-agent/resource-agent.component.json"
    if type_id not in ("model-provider", "calculator", "key-value-memory", "contextual-call"):
        raise ValueError("Browser fixture requires a registered descriptor")
    return ROOT / "components" / type_id / f"{type_id}.component.json"


def resource_operation(
    type_id: str, name: str, config: JsonObject, input_schema: JsonObject, output_schema: JsonObject
) -> tuple[JsonObject, JsonObject]:
    if type_id == "example.resource-agent" and name == "generate":
        operation = LLMCall.describe(config)[0]
        return operation.input_schema, operation.output_schema
    if type_id == "contextual-call" and name == "invoke":
        from slow_thinker_ii.contracts import json_object

        return json_object(config["input_schema"]), json_object(config["worker_output_schema"])
    return input_schema, output_schema
