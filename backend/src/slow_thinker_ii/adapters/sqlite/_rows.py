"""Stored values: UTC times as fixed-width text and JSON kept in its given key order.

Tables are `STRICT` with `NOT NULL` where a value is required, so column types are enforced
when rows are written; JSON columns are decoded with duplicate-key and finiteness checks.
"""

import json
import sqlite3
from datetime import UTC, datetime

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

TIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


def stamp(at: datetime) -> str:
    """An aware time as sortable UTC text with microseconds; naive times are refused."""
    if at.utcoffset() is None:
        raise ValueError("A stored time must be timezone-aware")
    return at.astimezone(UTC).strftime(TIME_FORMAT)


def dump(value: JsonValue) -> str:
    """Compact JSON that keeps object keys in their given order (schemas, payloads)."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def integer(row: sqlite3.Row, key: str) -> int:
    value: int = row[key]
    return value


def optional_integer(row: sqlite3.Row, key: str) -> int | None:
    value: int | None = row[key]
    return value


def text(row: sqlite3.Row, key: str) -> str:
    value: str = row[key]
    return value


def optional_text(row: sqlite3.Row, key: str) -> str | None:
    value: str | None = row[key]
    return value


def moment(row: sqlite3.Row, key: str) -> datetime:
    return datetime.strptime(text(row, key), TIME_FORMAT).replace(tzinfo=UTC)


def optional_moment(row: sqlite3.Row, key: str) -> datetime | None:
    return None if row[key] is None else moment(row, key)


def stored_object(row: sqlite3.Row, key: str) -> JsonObject:
    return json_object(decode_json(text(row, key)))


def optional_object(row: sqlite3.Row, key: str) -> JsonObject | None:
    return None if row[key] is None else stored_object(row, key)


def stored_value(row: sqlite3.Row, key: str) -> JsonValue:
    return decode_json(text(row, key))
