"""Run plans of fixture hosts: a chain of fixture nodes between a Trigger and an Output."""

from slow_thinker_ii.catalog import ComponentDeclaration, parse_declaration
from slow_thinker_ii.contracts import JsonObject
from slow_thinker_ii.graphs import RunPlan
from support.examples import journey_plan, step_one_catalog

LIMITS: JsonObject = {
    "max_activations": 10,
    "max_running_nodes": 4,
    "time_limit_seconds": 60,
    "budget_usd": "0.01",
}


def fixture_declaration() -> ComponentDeclaration:
    """`fixture@1.0.0`: a stateless host for both placements, outputs from `/outputs`."""
    schema: JsonObject = {
        "type": "object",
        "required": ["outputs"],
        "properties": {
            "mode": {"type": "string"},
            "outputs": {"type": "array", "items": {"type": "string"}},
        },
    }
    return parse_declaration(
        {
            "format": "slow-thinker.component/1",
            "type": "fixture",
            "version": "1.0.0",
            "label": "Fixture",
            "description": "A host for adapter tests.",
            "icon": "component",
            "placements": ["node", "output"],
            "state": "stateless",
            "ports": {"inputs": ["in"], "outputs_from": "/outputs"},
            "uses": [],
            "config_schema": schema,
            "initial_config": {"mode": "serve", "outputs": ["out"]},
            "ui": {"card": [], "sections": []},
        }
    )


def fixture_plan(*modes: str, embedded: str | None = None, time_limit_seconds: int = 60) -> RunPlan:
    """Story → one fixture node per mode, in a chain → Result; `embedded` adds an output host."""
    workers = [_worker(index, mode) for index, mode in enumerate(modes, start=1)]
    if embedded is not None:
        part: JsonObject = {"position": "output", "component": "fixture@1.0.0"}
        workers[-1]["embedded"] = [{**part, "config": _config(embedded)}]
    story: JsonObject = {
        "id": "story",
        "name": "Story",
        "component": "trigger@1.0.0",
        "config": {"message": "A cat."},
    }
    result: JsonObject = {
        "id": "result",
        "name": "Result",
        "component": "output@1.0.0",
        "config": {},
    }
    ids = ["story", *(f"w{index}" for index in range(1, len(modes) + 1)), "result"]
    pairs = zip(ids, ids[1:], strict=False)
    document: JsonObject = {
        "format": "slow-thinker.graph/1",
        "id": "fixtures",
        "name": "Fixtures",
        "limits": {**LIMITS, "time_limit_seconds": time_limit_seconds},
        "nodes": [story, *workers, result],
        "connections": [{"from": f"{a}.out", "to": f"{b}.in"} for a, b in pairs],
    }
    return journey_plan(document, step_one_catalog(fixture_declaration()))


def _worker(index: int, mode: str) -> JsonObject:
    return {
        "id": f"w{index}",
        "name": f"Worker {index}",
        "component": "fixture@1.0.0",
        "config": _config(mode),
    }


def _config(mode: str) -> JsonObject:
    return {"mode": mode, "outputs": ["out"]}
