"""Configuration-specialized operation schemas shared by inherited agent types."""

from slow_thinker_ii.contracts import JsonObject, json_object

from ._schemas import LocalSchemas


def routed_schemas(config: JsonObject) -> tuple[JsonObject, JsonObject]:
    worker_schema = json_object(config["worker_output_schema"])
    worker_schema.setdefault("$id", "urn:slow-thinker-ii:routed-worker-output")
    output = object_schema(
        {
            "status": {"const": "succeeded"},
            "port": {"enum": config["outputs"]},
            "value": worker_schema,
        }
    )
    return json_object(config["input_schema"]), output


def redirector_schemas(config: JsonObject) -> tuple[JsonObject, JsonObject]:
    value_schema = json_object(config["input_schema"])
    value_schema.setdefault("$id", "urn:slow-thinker-ii:redirector-input")
    return object_schema({"value": value_schema}), object_schema(
        {"port": {"enum": config["outputs"]}}
    )


def llm_output(config: JsonObject, schemas: LocalSchemas) -> JsonObject:
    output = json_object(config["output"])
    value: JsonObject = (
        {"type": "string"} if output["format"] == "text" else json_object(output["schema"])
    )
    value.setdefault("$id", "urn:slow-thinker-ii:llm-output")
    success = object_schema(
        {"status": {"const": "ok"}, "format": {"const": output["format"]}, "value": value}
    )
    branches = schemas.document("urn:slow-thinker-ii:contracts:llm-call-result:0.1-draft")["oneOf"]
    if not isinstance(branches, list):
        raise ValueError("Local result schema must declare envelope alternatives")
    return {"type": "object", "oneOf": [success, branches[-1]]}


def object_schema(properties: JsonObject) -> JsonObject:
    return {
        "type": "object",
        "properties": properties,
        "required": list(properties),
        "additionalProperties": False,
    }
