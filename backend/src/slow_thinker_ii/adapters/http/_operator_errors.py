"""Stable operator errors never expose exception messages, payloads or filesystem paths."""

from uuid import uuid4

from fastapi import Response

from slow_thinker_ii.application import CommandConflict, CoordinatorUnavailable, InvalidCursor
from slow_thinker_ii.contracts import encode_json


class OperatorError(Exception):
    def __init__(self, code: str, status: int) -> None:
        self.code, self.status = code, status
        super().__init__(code)


def operator_error(error: Exception) -> Response:
    code, status = error_code(error)
    return Response(
        encode_json(
            {
                "schema_version": "0.1-draft",
                "error": {
                    "code": code,
                    "message": code.replace("_", " "),
                    "request_id": uuid4().hex,
                },
            }
        ),
        status_code=status,
        media_type="application/json",
        headers={"cache-control": "no-store"},
    )


def error_code(error: Exception) -> tuple[str, int]:
    if isinstance(error, OperatorError):
        return error.code, error.status
    if isinstance(error, CommandConflict):
        return "command_conflict", 409
    if isinstance(error, InvalidCursor):
        return "invalid_cursor", 400
    if isinstance(error, CoordinatorUnavailable):
        return "backend_unavailable", 503
    return "operator_service_unavailable", 503
