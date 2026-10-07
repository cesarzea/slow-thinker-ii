"""Strict, bounded operator input: JSON object bodies, known fields and query parameters."""

import re
from collections.abc import Collection

from fastapi import Request, Response

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, encode_json

from ._bodies import JSON_MEDIA_TYPE, bounded_body, media_type
from ._operator_errors import OperatorError

_SIGNED = re.compile(r"-?[0-9]{1,18}")
_UNSIGNED = re.compile(r"[0-9]{1,18}")
_NUMBER = re.compile(r"[1-9][0-9]{0,8}")
MAX_NUMBER = 999_999_999  # versions and changes


async def json_body(request: Request, limit: int) -> JsonObject:
    """The body as a JSON object; an empty body counts as `{}`."""
    content = await bounded_body(request, limit)
    if content is None:
        raise OperatorError(413, "request_too_large", f"The request body exceeds {limit} bytes.")
    if not content:
        return {}
    if media_type(request) != JSON_MEDIA_TYPE or request.headers.getlist("content-encoding"):
        message = "Send the body as uncompressed JSON with Content-Type: application/json."
        raise OperatorError(415, "json_content_required", message)
    try:
        value = decode_json(content.decode("utf-8"))
    except (ValueError, RecursionError) as error:
        raise OperatorError(400, "invalid_json", "The request body is not valid JSON.") from error
    if not isinstance(value, dict):
        raise invalid_request("The request body must be a JSON object.")
    return value


def known_fields(
    body: JsonObject, required: Collection[str], optional: Collection[str] = ()
) -> None:
    """Refuses unknown and missing fields with `422 invalid_request`."""
    unknown = sorted(set(body) - {*required, *optional})
    if unknown:
        raise invalid_request(f"The field “{unknown[0]}” is not supported.")
    missing = [name for name in required if name not in body]
    if missing:
        raise invalid_request(f"The field “{missing[0]}” is required.")


async def document_field(request: Request, limit: int) -> JsonValue:
    """The `document` of a body that has exactly that field and no query parameters."""
    query(request)
    body = await json_body(request, limit)
    known_fields(body, ("document",))
    return body["document"]


def number_field(body: JsonObject, name: str) -> int:
    """A version or change number from 1."""
    number = body[name]
    if type(number) is not int or not 1 <= number <= MAX_NUMBER:
        raise invalid_request(f"The field “{name}” must be a whole number from 1.")
    return number


def start_field(body: JsonObject) -> tuple[str, int]:
    """The `from` of a new branch: exactly `{"version": n}` or `{"change": n}`."""
    start = body["from"]
    if not isinstance(start, dict) or len(start) != 1 or not set(start) <= {"version", "change"}:
        raise invalid_request("The field “from” must name exactly one version or one change.")
    kind = next(iter(start))
    return kind, number_field(start, kind)


def text_field(body: JsonObject, name: str) -> str:
    value = body[name]
    if not isinstance(value, str):
        raise invalid_request(f"The field “{name}” must be a string.")
    return value


def query(request: Request, allowed: Collection[str] = ()) -> dict[str, str]:
    """The query parameters; unknown or repeated ones are refused with `422 invalid_query`."""
    parameters = request.query_params
    for name in parameters:
        if name not in allowed or len(parameters.getlist(name)) > 1:
            raise invalid_query(f"The query parameter “{name}” is not supported here.")
    return dict(parameters)


def integer(parameters: dict[str, str], name: str, default: int, *, signed: bool = True) -> int:
    value = parameters.get(name)
    if value is None:
        return default
    pattern = _SIGNED if signed else _UNSIGNED
    if pattern.fullmatch(value) is None:
        kind = "an integer" if signed else "a non-negative integer"
        raise invalid_query(f"The query parameter “{name}” must be {kind}.")
    return int(value)


def numbered(text: str, kind: str, graph_id: str) -> int:
    """A `version` or `change` path segment; anything but a number from 1 names none."""
    if _NUMBER.fullmatch(text) is None:
        message = f"Graph “{graph_id}” has no {kind} {text}."
        raise OperatorError(404, f"{kind}_not_found", message)
    return int(text)


def reply(value: JsonValue, status: int = 200) -> Response:
    return Response(encode_json(value), status, media_type="application/json")


def invalid_request(message: str) -> OperatorError:
    return OperatorError(422, "invalid_request", message)


def invalid_query(message: str) -> OperatorError:
    return OperatorError(422, "invalid_query", message)
