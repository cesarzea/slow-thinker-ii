"""Contract examples and the step 1 configuration, read from the repository and never copied."""

import copy
from pathlib import Path
from typing import Literal

from slow_thinker_ii.catalog import (
    Catalog,
    ComponentDeclaration,
    LlmModelSettings,
    llm_entry,
    parse_declaration,
    platform_declarations,
)
from slow_thinker_ii.contracts import (
    JsonObject,
    JsonValue,
    decode_json,
    json_object,
    value_at_pointer,
)

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "docs/contracts").is_dir())
CONTRACTS = ROOT / "docs/contracts"
J1, J2, J3 = "funny-story", "story-triage", "funny-story-with-review"

type Temperature = Literal["unsupported", "supported", "without_reasoning"]


def example(name: str) -> JsonValue:
    return decode_json((CONTRACTS / "examples" / name).read_text(encoding="utf-8"))


def declaration_example(name: str) -> JsonObject:
    return json_object(example(f"{name}.component.json"))


def graph_example(name: str) -> JsonObject:
    return json_object(example(f"{name}.graph.json"))


def model_settings() -> tuple[LlmModelSettings, ...]:
    text = (ROOT / "examples/server-configuration.json").read_text(encoding="utf-8")
    models = value_at_pointer(decode_json(text), ("llm", "models"))
    assert isinstance(models, list)
    return tuple(_settings(json_object(model)) for model in models)


def _settings(model: JsonObject) -> LlmModelSettings:
    identifier, label, provider, name = (model[key] for key in ("id", "label", "provider", "model"))
    maximum, default = model["max_output_tokens"], model["default_output_tokens"]
    efforts, temperature = model["reasoning_efforts"], model["temperature"]
    assert isinstance(identifier, str) and isinstance(label, str) and isinstance(provider, str)
    assert isinstance(name, str) and isinstance(maximum, int) and isinstance(default, int)
    assert isinstance(efforts, list)
    effort_names = tuple(effort for effort in efforts if isinstance(effort, str))
    return LlmModelSettings(
        identifier, label, provider, name, maximum, default, effort_names, _temperature(temperature)
    )


def _temperature(value: JsonValue) -> Temperature:
    for option in ("unsupported", "supported", "without_reasoning"):
        if value == option:
            return option
    raise AssertionError(value)


def step_one_components() -> list[ComponentDeclaration]:
    packaged = [parse_declaration(declaration_example(name)) for name in ("llm-call", "router")]
    return [*platform_declarations(), *packaged]


def step_one_catalog(*extra: ComponentDeclaration) -> Catalog:
    entries = [llm_entry(settings) for settings in model_settings()]
    return Catalog([*step_one_components(), *extra], entries)


def changed(document: JsonObject, path: tuple[str | int, ...], value: JsonValue) -> JsonObject:
    """A deep copy of `document` with the value at `path` replaced or added."""
    result = copy.deepcopy(document)
    parent = value_at_pointer(result, path[:-1])
    if isinstance(parent, dict):
        parent[str(path[-1])] = value
    elif isinstance(parent, list):
        parent[int(path[-1])] = value
    return result


def without(document: JsonObject, path: tuple[str | int, ...]) -> JsonObject:
    """A deep copy of `document` without the member or item at `path`."""
    result = copy.deepcopy(document)
    parent = value_at_pointer(result, path[:-1])
    if isinstance(parent, dict):
        del parent[str(path[-1])]
    elif isinstance(parent, list):
        del parent[int(path[-1])]
    return result


def appended(document: JsonObject, path: tuple[str | int, ...], item: JsonValue) -> JsonObject:
    result = copy.deepcopy(document)
    target = value_at_pointer(result, path)
    assert isinstance(target, list)
    target.append(item)
    return result
