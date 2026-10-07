"""Declarations shipped inside the development packages of the components."""

import json
from importlib.resources import files

from slow_thinker_ii.contracts import JsonValue

PACKAGES = ("slow_thinker_llm_call", "slow_thinker_router", "slow_thinker_memory")


def development_declarations() -> tuple[JsonValue, ...]:
    documents: list[JsonValue] = []
    for package in PACKAGES:
        text = files(package).joinpath("component.json").read_text(encoding="utf-8")
        documents.append(json.loads(text))
    return tuple(documents)
