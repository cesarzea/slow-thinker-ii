"""Validate the closed initial report vocabulary and remove authentication material."""

import math
import re

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

_SECRET_KEYS = frozenset(
    {
        "authorization",
        "api_key",
        "apikey",
        "access_token",
        "token",
        "secret",
        "password",
        "invocation_grant",
        "invocation-grant",
        "credential",
        "credentials",
    }
)


def redact(value: JsonValue, grant: str) -> JsonValue:
    if isinstance(value, dict):
        return {
            key: {"status": "redacted", "reason": "authentication_material"}
            if key.lower().replace("-", "_") in _SECRET_KEYS
            else redact(item, grant)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item, grant) for item in value]
    if isinstance(value, str):
        value = value.replace(grant, "[redacted]")
        return re.sub(r"(?i)Bearer\s+[^\s]+|sk-[A-Za-z0-9_-]{8,}", "[redacted]", value)
    return value


def component_report(raw: str, grant: str, limit: int) -> JsonObject:
    if len(raw.encode()) > limit:
        raise ValueError("report_size_limit")
    value = json_object(decode_json(raw))
    required = {"kind", "schema_version", "value"}
    if not required <= set(value) or set(value) - required - {"source_occurred_at"}:
        raise ValueError("invalid_report_fields")
    if (
        value["kind"] not in ("progress", "state", "explanation", "reasoning")
        or value["schema_version"] != "1"
    ):
        raise ValueError("unsupported_report_schema")
    stamp = value.get("source_occurred_at")
    if "source_occurred_at" in value and (
        isinstance(stamp, bool) or not isinstance(stamp, int | float) or not math.isfinite(stamp)
    ):
        raise ValueError("invalid_report_timestamp")
    retained = redact(value["value"], grant)
    return {
        "kind": value["kind"],
        "schema_version": "1",
        "value": retained,
        "capture_status": "present" if retained == value["value"] else "redacted",
        "evidence": "reported",
        "source_occurred_at": stamp,
    }
