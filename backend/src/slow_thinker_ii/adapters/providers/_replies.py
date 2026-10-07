"""Provider replies: 200 with normalized usage, or the contract's 502 and 504 error bodies."""

from datetime import UTC, datetime

from slow_thinker_ii.application import ProviderReply
from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._capture import decoded, redacted_object, redacted_text
from ._endpoint import ProviderEndpoint
from ._usage import normalized_usage

MAX_DETAIL_CHARACTERS = 500


def utc_now() -> datetime:
    return datetime.now(UTC)


def error_reply(status: int, message: str, started: datetime) -> ProviderReply:
    """`{"error": {"code", "message", "type"}}`: 504 `provider_timeout`, else 502."""
    if status == 504:
        error: JsonObject = {
            "code": "provider_timeout",
            "message": message,
            "type": "timeout_error",
        }
    else:
        error = {"code": "provider_error", "message": message, "type": "provider_error"}
    return ProviderReply(status, {"error": error}, None, started, utc_now())


def response_reply(
    endpoint: ProviderEndpoint, status: int, raw: bytes, started: datetime
) -> ProviderReply:
    """A complete HTTP response: 200 with a JSON object body succeeds; anything else is 502,
    with the provider's status and its redacted message."""
    body = decoded(raw)
    if status == 200 and isinstance(body, dict):
        clean = redacted_object(body, endpoint.api_key)
        usage = normalized_usage(endpoint.provider, clean)
        return ProviderReply(200, clean, usage, started, utc_now())
    if status == 200:
        return error_reply(502, "The provider's response is not a JSON object.", started)
    detail = _provider_detail(body) or raw.decode("utf-8", errors="replace").strip()
    text = _shortened(redacted_text(detail, endpoint.api_key))
    return error_reply(502, f"The provider answered with HTTP {status}: {text}", started)


def _provider_detail(body: JsonValue) -> str | None:
    """The provider's own `error.message`, followed by its `error.code` when it gives one."""
    error = body.get("error") if isinstance(body, dict) else None
    if not isinstance(error, dict):
        return None
    message, code = error.get("message"), error.get("code")
    if not isinstance(message, str) or not message.strip():
        return None
    return f"{message} ({code})" if isinstance(code, str) and code else message


def _shortened(text: str) -> str:
    if not text:
        return "no details."
    if len(text) <= MAX_DETAIL_CHARACTERS:
        return text
    return text[: MAX_DETAIL_CHARACTERS - 1] + "…"
