"""Strict raw JSON and exact query identities for personal graph definitions."""

import re

from fastapi import Request
from pydantic import BaseModel, Field, ValidationError

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import decode_json

from ._operator_errors import OperatorError


class ReferenceBody(BaseModel, extra="forbid", strict=True):
    graph_id: str = Field(pattern=r"^[a-z][a-z0-9_.-]*$")
    revision: str = Field(min_length=1)


class DraftBody(BaseModel, extra="forbid", strict=True):
    source: ReferenceBody
    target: ReferenceBody


async def definition_source(request: Request, limit: int) -> str:
    if request.query_params:
        raise OperatorError("invalid_query", 400)
    if request.headers.getlist("content-encoding"):
        raise OperatorError("unsupported_transport_options", 400)
    content_types = request.headers.getlist("content-type")
    if (
        len(content_types) != 1
        or content_types[0].split(";")[0].strip().lower() != "application/json"
    ):
        raise OperatorError("json_content_required", 415)
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            raise OperatorError("request_too_large", 413)
        chunks.append(chunk)
    try:
        source = b"".join(chunks).decode("utf-8")
        decode_json(source)
        return source
    except (ValueError, RecursionError) as error:
        raise OperatorError("invalid_json", 400) from error


async def draft_body(
    request: Request, limit: int
) -> tuple[library.GraphReference, library.GraphReference]:
    source = await definition_source(request, limit)
    try:
        body = DraftBody.model_validate(decode_json(source))
    except ValidationError as error:
        raise OperatorError("invalid_definition", 422) from error
    return (
        library.GraphReference(body.source.graph_id, body.source.revision),
        library.GraphReference(body.target.graph_id, body.target.revision),
    )


def page_query(request: Request) -> tuple[int, str | None]:
    fields = query_fields(request, {"limit", "cursor"})
    raw_limit = fields.get("limit", "50")
    if not re.fullmatch(r"[0-9]{1,3}", raw_limit) or not 1 <= int(raw_limit) <= 100:
        raise OperatorError("invalid_query", 400)
    cursor = fields.get("cursor")
    if cursor == "":
        raise OperatorError("invalid_cursor", 400)
    return int(raw_limit), cursor


def detail_query(request: Request) -> library.GraphReference:
    fields = query_fields(request, {"graph_id", "revision"})
    graph_id, revision = fields.get("graph_id", ""), fields.get("revision", "")
    if not re.fullmatch(r"[a-z][a-z0-9_.-]*", graph_id) or not revision:
        raise OperatorError("invalid_query", 400)
    return library.GraphReference(graph_id, revision)


def query_fields(request: Request, allowed: set[str]) -> dict[str, str]:
    fields = request.query_params
    if set(fields) - allowed or any(len(fields.getlist(key)) != 1 for key in fields):
        raise OperatorError("invalid_query", 400)
    return dict(fields)
