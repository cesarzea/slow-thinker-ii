"""Contract examples and the step 1 server configuration, read from the repository, never copied."""

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
from slow_thinker_ii.graphs import RunPlan, compile_plan

ROOT = next(path for path in Path(__file__).resolve().parents if (path / "docs/contracts").is_dir())
EXAMPLES = ROOT / "docs/contracts/examples"
J1, J2, J3 = "funny-story", "story-triage", "funny-story-with-review"
LUNA, FLASH = "openai/gpt-6-luna", "deepseek/deepseek-flash"

type Temperature = Literal["unsupported", "supported", "without_reasoning"]


def graph_document(name: str) -> JsonObject:
    """The journey graph `name` (J1, J2 or J3) as a fresh, mutable document."""
    return json_object(decode_json((EXAMPLES / f"{name}.graph.json").read_text(encoding="utf-8")))


def server_configuration() -> JsonObject:
    text = (ROOT / "examples/server-configuration.json").read_text(encoding="utf-8")
    return json_object(decode_json(text))


def configured_models() -> list[JsonObject]:
    llm = json_object(server_configuration()["llm"])
    models = llm["models"]
    assert isinstance(models, list)
    return [json_object(model) for model in models]


def model_settings(model: JsonObject) -> LlmModelSettings:
    """The catalog settings of one configured model."""
    identifier, label, provider, name = (model[key] for key in ("id", "label", "provider", "model"))
    maximum, default, efforts = (
        model[key] for key in ("max_output_tokens", "default_output_tokens", "reasoning_efforts")
    )
    assert isinstance(identifier, str) and isinstance(label, str) and isinstance(provider, str)
    assert isinstance(name, str) and isinstance(maximum, int) and isinstance(default, int)
    assert isinstance(efforts, list)
    names = tuple(effort for effort in efforts if isinstance(effort, str))
    temperature = _temperature(model["temperature"])
    return LlmModelSettings(identifier, label, provider, name, maximum, default, names, temperature)


def step_one_components(*extra: ComponentDeclaration) -> list[ComponentDeclaration]:
    """Trigger, Output, LLM Call and Router, plus `extra` declarations."""
    packaged = [_declaration(name) for name in ("llm-call", "router")]
    return [*platform_declarations(), *packaged, *extra]


def memory_declaration() -> ComponentDeclaration:
    """`memory@1.0.0`, the Memory package's declaration."""
    return _declaration("memory")


def with_memory(document: JsonObject, node_id: str, max_exchanges: int = 10) -> JsonObject:
    """A copy of `document` whose node `node_id` has a Memory embedded as its memory."""
    result = copy.deepcopy(document)
    nodes = result["nodes"]
    assert isinstance(nodes, list)
    for node in nodes:
        if isinstance(node, dict) and node.get("id") == node_id:
            embedded = node.get("embedded")
            kept = list(embedded) if isinstance(embedded, list) else []
            memory: JsonObject = {"max_exchanges": max_exchanges}
            node["embedded"] = [
                *kept,
                {"position": "memory", "component": "memory@1.0.0", "config": memory},
            ]
    return result


def step_one_catalog(*extra: ComponentDeclaration) -> Catalog:
    entries = [llm_entry(model_settings(model)) for model in configured_models()]
    return Catalog(step_one_components(*extra), entries)


def journey_plan(document: JsonObject | str, catalog: Catalog | None = None) -> RunPlan:
    """The run plan of a journey (by name) or of a modified document, as version 1."""
    source = graph_document(document) if isinstance(document, str) else document
    return compile_plan(source, catalog or step_one_catalog(), 1)


def stateful_router() -> ComponentDeclaration:
    """`router@2.0.0`: the Router declared stateful, for `node_busy` checks."""
    document = _declaration_document("router")
    document["state"] = "stateful"
    document["version"] = "2.0.0"
    return parse_declaration(document)


def changed(document: JsonObject, path: tuple[str | int, ...], value: JsonValue) -> JsonObject:
    """A deep copy of `document` with the value at `path` replaced or added."""
    result = copy.deepcopy(document)
    parent = value_at_pointer(result, path[:-1])
    if isinstance(parent, list) and isinstance(path[-1], int):
        parent[path[-1]] = value
    elif isinstance(parent, dict):
        parent[str(path[-1])] = value
    return result


def _declaration_document(name: str) -> JsonObject:
    text = (EXAMPLES / f"{name}.component.json").read_text(encoding="utf-8")
    return json_object(decode_json(text))


def _declaration(name: str) -> ComponentDeclaration:
    return parse_declaration(_declaration_document(name))


def _temperature(value: JsonValue) -> Temperature:
    for option in ("unsupported", "supported", "without_reasoning"):
        if value == option:
            return option
    raise AssertionError(value)
