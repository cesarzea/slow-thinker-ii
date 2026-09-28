"""Native provider failures stay distinct from platform denial or an ineligible late result."""

from slow_thinker_ii.contracts import decode_json, encode_json, json_object

from ._dispatch_ports import ManagedResult
from ._native_records import GatewayError, NativeReply


def native_reply(result: ManagedResult) -> NativeReply:
    payload = json_object(decode_json(result.result.payload_json))
    if result.outcome.publish and not result.result.is_error:
        response = json_object(payload.get("response"))
        return NativeReply(200, encode_json(response), safe_header(payload.get("request_id")))
    if result.outcome.reason != "operation_failed" or not result.result.is_error:
        raise GatewayError("model_result_unavailable", 409)
    error = json_object(payload.get("error"))
    status = error.get("status")
    if error.get("origin") != "provider" or type(status) is not int or not 400 <= status <= 599:
        raise GatewayError("model_transport_failed")
    if "body" not in error:
        raise GatewayError("invalid_provider_error")
    return NativeReply(
        status,
        encode_json(error["body"]),
        safe_header(error.get("request_id")),
        safe_header(error.get("retry_after")),
    )


def safe_header(value: object) -> str | None:
    if (
        isinstance(value, str)
        and 0 < len(value) <= 256
        and all(32 <= ord(char) < 127 for char in value)
    ):
        return value
    return None
