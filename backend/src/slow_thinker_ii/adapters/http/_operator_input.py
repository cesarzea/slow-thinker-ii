"""Strict, bounded command envelopes contain intentions, never prepared runtime objects."""

from typing import Annotated, Literal

from fastapi import Request
from pydantic import BaseModel, Field, ValidationError

from slow_thinker_ii.contracts import JsonObject, decode_json, json_object

from ._operator_errors import OperatorError

Identity = Annotated[str, Field(min_length=1, max_length=128, pattern=r"^[a-zA-Z0-9_.-]+$")]


class CommandBody(BaseModel, extra="forbid", strict=True):
    schema_version: Literal["0.1-draft"]
    command_id: Identity


class SessionBody(CommandBody):
    name: str = Field(min_length=1, max_length=200)


class StartBody(CommandBody):
    session_id: Identity
    graph_id: Identity
    graph_revision: Identity
    configuration_revision: Identity
    input: JsonObject


async def command_body[T: BaseModel](request: Request, model: type[T], limit: int) -> T:
    if request.query_params or request.headers.getlist("content-encoding"):
        raise OperatorError("unsupported_transport_options", 400)
    if request.headers.get("content-type", "").split(";")[0].strip().lower() != "application/json":
        raise OperatorError("json_content_required", 415)
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            raise OperatorError("request_too_large", 413)
        chunks.append(chunk)
    try:
        value = json_object(decode_json(b"".join(chunks).decode("utf-8")))
        return model.model_validate(value)
    except ValidationError as error:
        raise OperatorError("invalid_command", 422) from error
    except ValueError as error:
        raise OperatorError("invalid_json", 400) from error
