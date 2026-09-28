"""Only bounded native requests with invocation credentials reach model routing."""

from fastapi import Request

from slow_thinker_ii.application import GatewayError


def invocation_grant(request: Request) -> str:
    if request.headers.getlist("origin"):
        raise GatewayError("browser_origin_denied", 403)
    excluded = {"openai-organization", "openai-project", "openai-beta", "content-encoding"}
    if request.query_params or excluded.intersection(request.headers):
        raise GatewayError("unsupported_transport_options", 400)
    values = request.headers.getlist("authorization")
    if len(values) != 1:
        raise GatewayError("invocation_authority_required", 401)
    scheme, separator, token = values[0].partition(" ")
    if (
        scheme.lower() != "bearer"
        or not separator
        or not token
        or any(char.isspace() for char in token)
    ):
        raise GatewayError("invocation_authority_required", 401)
    return token


async def request_body(request: Request, limit: int) -> str:
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type != "application/json":
        raise GatewayError("json_content_required", 415)
    chunks: list[bytes] = []
    size = 0
    async for chunk in request.stream():
        size += len(chunk)
        if size > limit:
            raise GatewayError("request_too_large", 413)
        chunks.append(chunk)
    return b"".join(chunks).decode("utf-8")
