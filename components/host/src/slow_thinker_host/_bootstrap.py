"""Read the platform's bootstrap document, the host's only configuration input."""

import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

from ._json import JsonObject, JsonValue, decode_json, json_object
from ._protocol import BOOTSTRAP_FORMAT, Position

_FIELDS = ("format", "component", "node", "position", "config", "platform", "limits")


@dataclass(frozen=True)
class Bootstrap:
    """The launch parameters of one host: its component, node, configuration and platform."""

    component: str
    node_id: str
    node_name: str
    position: Position
    config: dict[str, JsonValue]
    llm_base_url: str
    mcp_url: str
    max_concurrent_invocations: int


def read_bootstrap(path: Path) -> Bootstrap:
    """Parse a `slow-thinker.bootstrap/1` document; any deviation raises ValueError."""
    record = _fields(json_object(decode_json(path.read_text(encoding="utf-8"))), _FIELDS)
    if record["format"] != BOOTSTRAP_FORMAT:
        raise ValueError(f"Unsupported bootstrap format: {record['format']!r}")
    component = _text(record["component"], "component")
    if re.fullmatch(r"[a-z][a-z0-9-]{0,63}@\d+\.\d+\.\d+", component) is None:
        raise ValueError(f"Invalid component reference: {component!r}")
    node = _fields(json_object(record["node"]), ("id", "name"))
    platform = _fields(json_object(record["platform"]), ("llm_base_url", "mcp_url"))
    limits = _fields(json_object(record["limits"]), ("max_concurrent_invocations",))
    return Bootstrap(
        component=component,
        node_id=_text(node["id"], "node id"),
        node_name=_text(node["name"], "node name"),
        position=_position(record["position"]),
        config=json_object(record["config"]),
        llm_base_url=_url(platform["llm_base_url"], "llm_base_url"),
        mcp_url=_url(platform["mcp_url"], "mcp_url"),
        max_concurrent_invocations=_positive(limits["max_concurrent_invocations"]),
    )


def _fields(record: JsonObject, names: tuple[str, ...]) -> JsonObject:
    if set(record) != set(names):
        raise ValueError(f"Bootstrap object fields must be exactly: {', '.join(names)}")
    return record


def _text(value: JsonValue, name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"The bootstrap {name} must be a non-empty string")
    return value


def _position(value: JsonValue) -> Position:
    if value == "node":
        return "node"
    if value == "output":
        return "output"
    if value == "memory":
        return "memory"
    raise ValueError(f"Unsupported bootstrap position: {value!r}")


def _url(value: JsonValue, name: str) -> str:
    url = urlsplit(_text(value, name))
    if url.scheme not in ("http", "https") or not url.hostname or url.port == 0:
        raise ValueError(f"The bootstrap {name} must be an HTTP URL")
    if url.username or url.password or url.query or url.fragment:
        raise ValueError(f"The bootstrap {name} must not carry credentials, queries or fragments")
    return url.geturl()


def _positive(value: JsonValue) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError("max_concurrent_invocations must be a positive integer")
    return value
