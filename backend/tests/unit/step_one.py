"""Tariffs of the step 1 server configuration, read from the reference example."""

import copy
from pathlib import Path

from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    decode_json,
    json_object,
    value_at_pointer,
)

LUNA = "openai/gpt-6-luna"
FLASH = "deepseek/deepseek-flash"
CONFIGURATION = "examples/server-configuration.json"


def _repository() -> Path:
    # Also found from the copy of the tests that mutation testing runs under backend/mutants.
    here = Path(__file__).resolve()
    return next(parent for parent in here.parents if (parent / CONFIGURATION).is_file())


def step_one_tariff(model_id: str) -> JsonObject:
    text = (_repository() / CONFIGURATION).read_text(encoding="utf-8")
    models = value_at_pointer(decode_json(text), ("llm", "models"))
    assert isinstance(models, list)
    model = next(json_object(item) for item in models if json_object(item)["id"] == model_id)
    return json_object(model["tariff"])


def changed(document: JsonObject, path: tuple[str | int, ...], value: JsonValue) -> JsonObject:
    """A deep copy of `document` with the value at `path` replaced or added."""
    result = copy.deepcopy(document)
    parent = value_at_pointer(result, path[:-1])
    if isinstance(parent, dict):
        parent[str(path[-1])] = value
    elif isinstance(parent, list):
        parent[int(path[-1])] = value
    return result


def removed(document: JsonObject, *keys: str) -> JsonObject:
    result = copy.deepcopy(document)
    for key in keys:
        del result[key]
    return result
