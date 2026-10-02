"""Independent key/value operations with transactional bounded namespace state."""

from pathlib import Path

from slow_thinker_host import JsonObject, JsonValue, decode_json

from . import _store
from ._validation import bounded_integer, check_version, key, precondition, request, value_text


class KeyValueMemory:
    def __init__(
        self,
        path: Path,
        namespace: str,
        *,
        max_entries: int = 1000,
        max_value_bytes: int = 65536,
    ) -> None:
        if type(namespace) is not str or not namespace:
            raise ValueError("Memory namespace must be nonempty")
        self._path, self._namespace = path, namespace
        self._entries = bounded_integer(max_entries, 10000)
        self._bytes = bounded_integer(max_value_bytes, 65536)

    def get(self, arguments: JsonObject) -> JsonObject:
        request(arguments, {"key"}, set())
        selected = key(arguments["key"])
        with _store.transaction(self._path) as connection:
            entry = _store.entry(connection, self._namespace, selected)
        if entry is None:
            return {"found": False, "value": None, "version": None}
        text, version = entry
        if len(text.encode("utf-8")) > self._bytes:
            raise ValueError("Stored memory value exceeds the configured bound")
        return {"found": True, "value": decode_json(text), "version": version}

    def put(self, arguments: JsonObject) -> JsonObject:
        request(arguments, {"key", "value"}, {"expected_version"})
        selected, text = key(arguments["key"]), value_text(arguments["value"], self._bytes)
        expected = precondition(arguments)
        with _store.transaction(self._path) as connection:
            current = _store.entry(connection, self._namespace, selected)
            check_version(expected, None if current is None else current[1])
            if current is None and _store.count(connection, self._namespace) >= self._entries:
                raise ValueError("memory_capacity_exceeded")
            version = _store.next_version(connection, self._namespace)
            connection.execute(
                "INSERT INTO memory_entries(namespace,key,value_json,version) VALUES(?,?,?,?) "
                "ON CONFLICT(namespace,key) DO UPDATE SET value_json=excluded.value_json, "
                "version=excluded.version",
                (self._namespace, selected, text, version),
            )
        return {"version": version}

    def delete(self, arguments: JsonObject) -> JsonObject:
        request(arguments, {"key"}, {"expected_version"})
        selected, expected = key(arguments["key"]), precondition(arguments)
        with _store.transaction(self._path) as connection:
            current = _store.entry(connection, self._namespace, selected)
            check_version(expected, None if current is None else current[1])
            connection.execute(
                "DELETE FROM memory_entries WHERE namespace=? AND key=?",
                (self._namespace, selected),
            )
        return {"deleted": current is not None}

    def list(self, arguments: JsonObject) -> JsonObject:
        request(arguments, set(), {"limit", "after"})
        limit = bounded_integer(arguments.get("limit", 100), 100)
        after = key(arguments["after"]) if "after" in arguments else ""
        with _store.transaction(self._path) as connection:
            rows = _store.keys(connection, self._namespace, after, limit + 1)
        items: list[JsonValue] = [
            {"key": name, "version": version} for name, version in rows[:limit]
        ]
        return {"items": items, "next_key": rows[limit - 1][0] if len(rows) > limit else None}
