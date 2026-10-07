"""Only bounded, non-browser requests carrying an invocation grant reach the use cases."""

from fastapi import Request

from ._bodies import JSON_MEDIA_TYPE, bounded_body, media_type
from ._native_errors import INVALID_GRANT, GatewayRefusal

_EXCLUDED = frozenset({"openai-organization", "openai-project", "openai-beta", "content-encoding"})


def invocation_grant(request: Request) -> str:
    """The bearer grant; browsers, query strings and provider account options are refused."""
    if request.headers.getlist("origin"):
        message = "Browser requests cannot use component endpoints."
        raise GatewayRefusal(403, "browser_origin_denied", message)
    if request.query_params or _EXCLUDED.intersection(request.headers):
        message = (
            "Query parameters, content encodings and OpenAI account headers are not supported."
        )
        raise GatewayRefusal(400, "invalid_request", message)
    values = request.headers.getlist("authorization")
    scheme, separator, token = values[0].partition(" ") if len(values) == 1 else ("", "", "")
    if scheme.lower() != "bearer" or not separator or not token or _has_space(token):
        raise GatewayRefusal(401, "invalid_grant", INVALID_GRANT)
    return token


async def request_body(request: Request, limit: int) -> str:
    """The bounded JSON request text, passed on unparsed."""
    if media_type(request) != JSON_MEDIA_TYPE:
        message = "Send the request as JSON with Content-Type: application/json."
        raise GatewayRefusal(415, "unsupported_media_type", message)
    content = await bounded_body(request, limit)
    if content is None:
        message = f"The request body exceeds {limit} bytes."
        raise GatewayRefusal(413, "request_too_large", message)
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as error:
        message = "The request body is not valid UTF-8."
        raise GatewayRefusal(400, "invalid_request", message) from error


def _has_space(token: str) -> bool:
    return any(character.isspace() for character in token)
