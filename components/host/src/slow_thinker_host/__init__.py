"""Public, optional SDK for independently installed MCP component hosts."""

from ._bootstrap import Bootstrap, read_bootstrap
from ._contracts import HostedComponent, Invocation, Operation, ToolReply
from ._json import JsonObject, JsonValue, decode_json, encode_json, json_object, json_value
from ._schemas import check_schema, validate_value
from ._server import DEADLINE_META, GRANT_META, PROTOCOL_VERSION, create_server, run_stdio

__all__ = [
    "Bootstrap",
    "read_bootstrap",
    "GRANT_META",
    "DEADLINE_META",
    "PROTOCOL_VERSION",
    "HostedComponent",
    "Invocation",
    "Operation",
    "ToolReply",
    "JsonObject",
    "JsonValue",
    "decode_json",
    "encode_json",
    "json_object",
    "json_value",
    "check_schema",
    "validate_value",
    "create_server",
    "run_stdio",
]
