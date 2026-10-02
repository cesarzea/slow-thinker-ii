"""Bound provider evidence and redact credentials before it leaves the trusted resource."""

import httpx2
from slow_thinker_host import JsonObject, JsonValue, ToolReply, decode_json


class CaptureLimit(ValueError):
    pass


async def read_body(response: httpx2.Response, limit: int) -> str:
    chunks: list[bytes] = []
    size = 0
    async for chunk in response.aiter_bytes(chunk_size=min(limit + 1, 16_384)):
        size += len(chunk)
        if size > limit:
            raise CaptureLimit("Provider response exceeds the capture limit")
        chunks.append(chunk)
    return b"".join(chunks).decode("utf-8", errors="replace")


def redact(value: JsonValue, secret: str) -> JsonValue:
    if isinstance(value, str):
        return value.replace(secret, "[redacted]")
    if isinstance(value, list):
        return [redact(item, secret) for item in value]
    if isinstance(value, dict):
        return {
            key.replace(secret, "[redacted]"): redact(item, secret) for key, item in value.items()
        }
    return value


def provider_reply(response: httpx2.Response, raw: str, secret: str) -> ToolReply:
    try:
        body = decode_json(raw)
    except ValueError:
        body = raw
    clean = redact(body, secret)
    headers, redacted = metadata(response, secret, clean != body)
    request_id = headers.get("x-request-id")
    if response.status_code == 200 and isinstance(clean, dict):
        return ToolReply(
            {
                "response": clean,
                "request_id": request_id,
                "redacted": redacted,
                "response_headers": headers,
            }
        )
    error: JsonObject = {
        "origin": "provider" if 400 <= response.status_code <= 599 else "protocol",
        "status": response.status_code,
        "body": clean,
        "request_id": request_id,
        "retry_after": headers.get("retry-after"),
    }
    return ToolReply(
        {"error": error, "redacted": redacted, "response_headers": headers}, is_error=True
    )


def transport_failure(code: str) -> ToolReply:
    return ToolReply({"error": {"origin": "transport", "code": code}}, is_error=True)


def metadata(response: httpx2.Response, secret: str, redacted: bool) -> tuple[JsonObject, bool]:
    headers: JsonObject = {
        name.replace(secret, "[redacted]"): value.replace(secret, "[redacted]")
        for name, value in response.headers.items()
    }
    redacted = redacted or any(
        secret in name or secret in value for name, value in response.headers.items()
    )
    return headers, redacted
