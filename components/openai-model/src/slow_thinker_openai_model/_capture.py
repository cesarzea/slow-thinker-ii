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
    request_id = response.headers.get("x-request-id")
    retry_after = response.headers.get("retry-after")
    redacted = clean != body or any(
        secret in item for item in (request_id or "", retry_after or "")
    )
    request_id = None if request_id is None else request_id.replace(secret, "[redacted]")
    if response.status_code == 200 and isinstance(clean, dict):
        return ToolReply({"response": clean, "request_id": request_id, "redacted": redacted})
    origin = "provider" if 400 <= response.status_code <= 599 else "protocol"
    error: JsonObject = {
        "origin": origin,
        "status": response.status_code,
        "body": clean,
        "request_id": request_id,
        "retry_after": None if retry_after is None else retry_after.replace(secret, "[redacted]"),
    }
    return ToolReply({"error": error, "redacted": redacted}, is_error=True)


def transport_failure(code: str) -> ToolReply:
    return ToolReply({"error": {"origin": "transport", "code": code}}, is_error=True)
