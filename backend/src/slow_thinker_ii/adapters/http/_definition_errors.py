"""Definition errors expose fixed codes and bounded diagnostics, never exception text."""

from uuid import uuid4

from fastapi import Response

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json

from ._operator_errors import OperatorError

_STATUSES = {
    "invalid_json": 400,
    "invalid_query": 400,
    "invalid_cursor": 400,
    "unsupported_transport_options": 400,
    "definition_not_found": 404,
    "definition_conflict": 409,
    "request_too_large": 413,
    "response_too_large": 413,
    "json_content_required": 415,
    "invalid_definition": 422,
    "definition_parent_missing": 422,
    "operator_service_unavailable": 503,
}


def definition_error(error: Exception) -> Response:
    code = "operator_service_unavailable"
    if isinstance(error, (library.DefinitionError, OperatorError)) and error.code in _STATUSES:
        code = error.code
    details: JsonObject = {
        "code": code,
        "message": code.replace("_", " "),
        "request_id": uuid4().hex,
    }
    if code == "invalid_definition" and isinstance(error, library.DefinitionError):
        details["issues"] = issue_data(error.issues)
    return Response(
        bounded_error_content(details),
        status_code=_STATUSES[code],
        media_type="application/json",
        headers={"cache-control": "no-store"},
    )


def bounded_error_content(details: JsonObject) -> str:
    value: JsonObject = {"schema_version": "0.1-draft", "error": details}
    content = encode_json(value)
    issues = details.get("issues")
    while len(content.encode("utf-8")) > 4096 and isinstance(issues, list) and issues:
        issues.pop()
        content = encode_json(value)
    return content


def issue_data(issues: tuple[library.DefinitionIssue, ...]) -> list[JsonValue]:
    result: list[JsonValue] = []
    for issue in issues[:10]:
        if len(issue.pointer) <= 160 and len(issue.message) <= 160:
            result.append({"pointer": issue.pointer, "message": issue.message})
        else:
            result.append({"pointer": "", "message": "The definition is invalid."})
    return result
