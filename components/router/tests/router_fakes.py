"""Router configurations, bootstrap documents and a context that records reports."""

from openai import AsyncOpenAI
from slow_thinker_host import JsonObject, JsonValue
from slow_thinker_router import Router, load_route, parse_config

REVIEW = """def route(received, node_input):
    if received["score"] >= 7:
        return "accepted", node_input
    return "revise", node_input
"""


def config(script: str = REVIEW, outputs: tuple[str, ...] = ("accepted", "revise")) -> JsonObject:
    return {"outputs": list(outputs), "script": script}


def router(script: str = REVIEW, outputs: tuple[str, ...] = ("accepted", "revise")) -> Router:
    settings = parse_config(config(script, outputs))
    return Router(settings, load_route(settings.script))


def bootstrap_document(position: str = "output", script: str = REVIEW) -> JsonObject:
    return {
        "format": "slow-thinker.bootstrap/1",
        "component": "router@1.0.0",
        "node": {"id": "reviewer", "name": "Reviewer"},
        "position": position,
        "config": config(script),
        "platform": {
            "llm_base_url": "http://127.0.0.1:9/v1",
            "mcp_url": "http://127.0.0.1:9/mcp",
        },
        "limits": {"max_concurrent_invocations": 4},
    }


class FakeContext:
    """Records reports; the Router never uses the LLM service."""

    def __init__(self) -> None:
        self.reports: list[tuple[str, JsonValue]] = []

    @property
    def activation_id(self) -> str:
        return "a1"

    def remaining_seconds(self) -> float:
        return 5.0

    async def report(self, kind: str, content: JsonValue) -> None:
        self.reports.append((kind, content))

    def llm_client(self) -> AsyncOpenAI:
        raise AssertionError("The Router does not call LLMs")
