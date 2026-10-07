"""Memory bootstrap documents and a context the Memory never needs."""

from openai import AsyncOpenAI
from slow_thinker_host import JsonObject, JsonValue


def bootstrap_document(position: str = "memory", max_exchanges: JsonValue = 2) -> JsonObject:
    return {
        "format": "slow-thinker.bootstrap/1",
        "component": "memory@1.0.0",
        "node": {"id": "interviewer", "name": "Interviewer"},
        "position": position,
        "config": {"max_exchanges": max_exchanges},
        "platform": {
            "llm_base_url": "http://127.0.0.1:9/v1",
            "mcp_url": "http://127.0.0.1:9/mcp",
        },
        "limits": {"max_concurrent_invocations": 4},
    }


class FakeContext:
    """The Memory neither reports nor calls LLMs."""

    @property
    def activation_id(self) -> str:
        return "a1"

    def remaining_seconds(self) -> float:
        return 5.0

    async def report(self, kind: str, content: JsonValue) -> None:
        raise AssertionError("The Memory does not report")

    def llm_client(self) -> AsyncOpenAI:
        raise AssertionError("The Memory does not call LLMs")
