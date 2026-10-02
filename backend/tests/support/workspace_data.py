"""Shared discovery inputs retain real descriptors and synthetic resource references."""

import time
from pathlib import Path

from slow_thinker_ii.contracts import JsonObject, JsonValue, decode_json, json_object

from .sequence_plans import ROOT

PACKAGES = ("model-provider", "calculator", "key-value-memory", "contextual-call")


def objects(value: JsonValue) -> tuple[JsonObject, ...]:
    assert isinstance(value, list)
    return tuple(json_object(item) for item in value)


def field_strings(value: JsonValue, name: str) -> set[str]:
    result: set[str] = set()
    for item in objects(value):
        field = item[name]
        assert isinstance(field, str)
        result.add(field)
    return result


def workspace_descriptors(root: Path = ROOT) -> tuple[str, ...]:
    paths = [root / "components" / name / f"{name}.component.json" for name in PACKAGES]
    paths.append(root / "examples/resource-agent/resource-agent.component.json")
    return tuple(path.read_text(encoding="utf-8") for path in paths)


def workspace_resources(root: Path = ROOT) -> JsonObject:
    sources = (
        *(
            path.read_text()
            for path in sorted((root / "docs/contracts/examples").glob("*.component.json"))
        ),
        *workspace_descriptors(root),
    )
    choices: list[JsonValue] = []
    for index, source in enumerate(sources):
        value = json_object(decode_json(source))
        choices.append(
            {
                "type_id": value["type_id"],
                "type_version": value["type_version"],
                "resolution_id": f"{index:032x}",
                "host_adapter": "fixture",
            }
        )
    return {
        "schema_version": "1",
        "installations": choices,
        "providers": {
            "illustrative-provider": provider("openai", "gpt-6-luna"),
            "openai-luna": provider("openai", "gpt-6-luna"),
            "deepseek-flash": provider("deepseek", "deepseek-flash"),
        },
    }


def provider(name: str, model: str) -> JsonObject:
    billing = (
        "openai.gpt-6-luna.standard.text.v1" if name == "openai" else "deepseek.flash.direct.v1"
    )
    return {
        "provider": name,
        "billing_profile": billing,
        "model": model,
        "returned_models": [model],
        "credential_ref": "synthetic-reference",
        "default_output_tokens": 256,
        "maximum_output_tokens": 4096,
        "review_expires_at": int(time.time()) + 86400 * 30,
        "maximum_tariff_age_seconds": 86400,
    }
