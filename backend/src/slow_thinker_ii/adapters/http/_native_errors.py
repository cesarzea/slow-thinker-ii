"""Refusals of component requests use the LLM service error body and never pass as replies."""

from types import MappingProxyType

from fastapi import Response

from slow_thinker_ii.contracts import JsonObject, encode_json

_TYPES = MappingProxyType(
    {
        400: "invalid_request_error",
        401: "authentication_error",
        403: "permission_error",
        413: "invalid_request_error",
        415: "invalid_request_error",
    }
)
INVALID_GRANT = "The grant is missing, unknown or expired."


class GatewayRefusal(Exception):
    """A component request refused by the adapter before it reaches a use case."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def refusal_reply(refusal: GatewayRefusal) -> Response:
    """`{"error": {"code", "message", "type"}}`, as the LLM service contract shapes errors."""
    kind = _TYPES.get(refusal.status, "invalid_request_error")
    body: JsonObject = {"error": {"code": refusal.code, "message": refusal.message, "type": kind}}
    return Response(encode_json(body), refusal.status, media_type="application/json")
