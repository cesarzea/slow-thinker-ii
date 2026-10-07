"""Operator API errors: `{"error": {"code", "message", "diagnostics"?}}`, never internals."""

from fastapi import Request, Response

from slow_thinker_ii.application import (
    BranchExists,
    BranchNotFound,
    ChangeNotFound,
    GraphExists,
    GraphInvalid,
    GraphNotFound,
    InvalidBranch,
    RunNotFound,
    TooManyRuns,
    VersionNotFound,
)
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json

PREFIX = "/api/v2"
ACCESS = "/access"  # GET {PREFIX}{ACCESS} reports the authentication mode and needs no token
MAX_MESSAGE = 2000  # characters; the interface refuses longer messages
INVALID_DOCUMENT = "The graph document has errors; see the diagnostics."
INTERNAL = "The server could not complete the request."


class OperatorError(Exception):
    """A refusal by the adapter itself, with its status, code and English message."""

    def __init__(self, status: int, code: str, message: str) -> None:
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


_APPLICATION: tuple[tuple[type[Exception], int, str], ...] = (
    (GraphExists, 409, "graph_exists"),
    (GraphNotFound, 404, "graph_not_found"),
    (VersionNotFound, 404, "version_not_found"),
    (ChangeNotFound, 404, "change_not_found"),
    (BranchNotFound, 404, "branch_not_found"),
    (BranchExists, 409, "branch_exists"),
    (InvalidBranch, 422, "invalid_request"),
    (RunNotFound, 404, "run_not_found"),
    (TooManyRuns, 409, "too_many_runs"),
)
OPERATOR_ERRORS: tuple[type[Exception], ...] = (
    OperatorError,
    GraphInvalid,
    *(kind for kind, _, _ in _APPLICATION),
)


def operator_path(path: str) -> bool:
    return path == PREFIX or path.startswith(f"{PREFIX}/")


def operator_error(error: Exception) -> Response:
    """The envelope of an `OPERATOR_ERRORS` exception; application messages are English."""
    if isinstance(error, OperatorError):
        return envelope(error.status, error.code, error.message)
    if isinstance(error, GraphInvalid):
        diagnostics: list[JsonValue] = [item.document() for item in error.diagnostics]
        return envelope(422, "invalid_document", INVALID_DOCUMENT, diagnostics)
    status, code = next(
        (status, code) for kind, status, code in _APPLICATION if isinstance(error, kind)
    )
    return envelope(status, code, str(error))


def envelope(
    status: int, code: str, message: str, diagnostics: list[JsonValue] | None = None
) -> Response:
    if len(message) > MAX_MESSAGE:
        message = f"{message[: MAX_MESSAGE - 1]}…"
    error: JsonObject = {"code": code, "message": message}
    if diagnostics is not None:
        error["diagnostics"] = diagnostics
    return Response(encode_json({"error": error}), status, media_type="application/json")


async def operator_reply(request: Request, error: Exception) -> Response:
    """Exception handler for `OPERATOR_ERRORS` raised by operator routes."""
    del request
    return operator_error(error)


async def internal_error(request: Request, error: Exception) -> Response:
    """Exception handler for unexpected failures: a bounded body; the server logs the error."""
    del error
    if operator_path(request.url.path):
        reply = envelope(500, "internal_error", INTERNAL)
        reply.headers["cache-control"] = "no-store"
        return reply
    body: JsonObject = {
        "error": {"code": "internal_error", "message": INTERNAL, "type": "api_error"}
    }
    return Response(encode_json(body), 500, media_type="application/json")
