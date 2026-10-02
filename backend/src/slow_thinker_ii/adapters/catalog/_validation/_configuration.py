"""Apply the published LLMCall configuration policy without importing provider SDKs."""

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_object

from .._models import ComponentRecord
from ._diagnostics import pointer, require
from ._schemas import resource, schema_children

RESERVED_PARAMETERS = frozenset(
    {
        "model",
        "messages",
        "stream",
        "response_format",
        "n",
        "base_url",
        "api_key",
        "timeout",
        "max_retries",
    }
)
LLM_CONFIG = "urn:slow-thinker-ii:contracts:llm-call-config:0.1-draft"


def configured_policy(identity: str, component: ComponentRecord, manifest: JsonObject) -> None:
    if not uses_llm_contract(json_object(manifest["config_schema"])):
        return
    parameters = json_object(component.config["parameters"])
    require(
        not RESERVED_PARAMETERS.intersection(parameters),
        pointer(("components", identity, "config", "parameters")),
        "Generation parameters cannot contain reserved credential, routing or lifecycle fields.",
    )
    for name, schema in schema_children(component.config):
        path = pointer(("components", identity, "config", *name.split("/")))
        require(
            fragments_only(schema),
            path,
            "Configured LLMCall schemas must use local fragment references only.",
        )


def uses_llm_contract(schema: JsonValue) -> bool:
    if isinstance(schema, dict) and schema.get("$ref") == LLM_CONFIG:
        return True
    return any(uses_llm_contract(item.contents) for item in resource(schema).subresources())


def fragments_only(schema: JsonValue) -> bool:
    if isinstance(schema, dict):
        for name in ("$ref", "$dynamicRef"):
            value = schema.get(name)
            if isinstance(value, str) and not value.startswith("#"):
                return False
    return all(fragments_only(item.contents) for item in resource(schema).subresources())
