"""Editable domain fixtures preserve exact values and the trusted bundled parent."""

from slow_thinker_ii.application import library
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from slow_thinker_ii.definitions import read_pointer

from ..sequence_plans import graph_value

PARENT = library.GraphReference("single-agent", "example-2")


def variant(
    revision: str, instructions: str = "Use the saved personal instructions."
) -> JsonObject:
    value = graph_value("single-agent")
    value["revision"] = revision
    value["derived_from"] = {"graph_id": PARENT.graph_id, "revision": PARENT.revision}
    set_field(value, "/components/proposer/config", "instructions", instructions)
    return value


def source(revision: str, instructions: str = "Use the saved personal instructions.") -> str:
    return encode_json(variant(revision, instructions))


def set_field(value: JsonObject, parent: str, name: str, replacement: JsonValue) -> None:
    target = read_pointer(value, parent)
    assert isinstance(target, dict)
    target[name] = replacement


def numeric_source(revision: str = "numeric α / version") -> str:
    value = variant(revision)
    set_field(
        value,
        "/components/proposer/config",
        "parameters",
        {"temperature": 1.0, "seed": 9007199254740993},
    )
    return encode_json(value)
