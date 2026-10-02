"""Validate external descriptors against the same trusted local schema registry."""

from pathlib import Path

from slow_thinker_ii.contracts import JsonObject, json_object

from ._validation._schemas import LocalSchemas


def validate_component_descriptor(value: JsonObject, schema_directory: Path) -> None:
    schemas = LocalSchemas(schema_directory)
    schemas.validate(value, schemas.component, ())
    schemas.schema(json_object(value["config_schema"]), "/config_schema")
    for name, item in json_object(value["operations"]).items():
        operation = json_object(item)
        if operation["mcp_tool"] != name:
            raise ValueError("Operation names must equal their managed MCP tool names")
        for field in ("input_schema", "output_schema"):
            schemas.schema(json_object(operation[field]), f"/operations/{name}/{field}")
