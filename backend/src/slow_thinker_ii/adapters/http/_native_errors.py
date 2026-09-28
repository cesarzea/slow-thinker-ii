"""Bounded platform failures cannot impersonate actual provider responses."""

from fastapi import Response

from slow_thinker_ii.access import AccessDenied
from slow_thinker_ii.accounting import BudgetExceeded
from slow_thinker_ii.application import GatewayError, RecordingError
from slow_thinker_ii.contracts import JsonObject, encode_json


def platform_error(error: Exception) -> Response:
    code, status = error_code(error)
    payload: JsonObject = {
        "error": {
            "message": code,
            "type": "platform_error",
            "code": code,
            "param": None,
            "origin": "platform",
        }
    }
    return Response(encode_json(payload), status_code=status, media_type="application/json")


def error_code(error: Exception) -> tuple[str, int]:
    if isinstance(error, GatewayError):
        return error.code, error.status
    if isinstance(error, AccessDenied):
        return "invocation_authority_denied", 403
    if isinstance(error, BudgetExceeded):
        return "budget_denied", 429
    if isinstance(error, RecordingError):
        return "recording_unavailable", 503
    if isinstance(error, TimeoutError):
        return "invocation_deadline", 408
    if isinstance(error, ValueError):
        return "invalid_model_request", 400
    return "model_gateway_failure", 502
