"""A fake host context whose LLM client reaches an in-memory Chat Completions endpoint."""

import httpx2
from openai import AsyncOpenAI
from slow_thinker_host import JsonObject, JsonValue, decode_json, json_object

SCORE: JsonObject = {
    "type": "object",
    "additionalProperties": False,
    "required": ["score"],
    "properties": {"score": {"type": "integer", "minimum": 1, "maximum": 10}},
}


def config(**changes: JsonValue) -> JsonObject:
    """The Proposer configuration of the funny-story journey, with `changes` applied."""
    base: JsonObject = {
        "prompt": "Rewrite this story so that it is funny. Keep it under 80 words.",
        "model": {"llm": "openai/gpt-6-luna", "parameters": {"max_completion_tokens": 300}},
        "input_format": None,
        "output_format": {"type": "text"},
    }
    return {**base, **changes}


def completion(content: str | None) -> JsonObject:
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "created": 1,
        "model": "openai/gpt-6-luna",
        "choices": [
            {
                "index": 0,
                "finish_reason": "stop",
                "message": {"role": "assistant", "content": content},
            }
        ],
    }


def platform_error(code: str, message: str) -> JsonObject:
    return {"error": {"code": code, "message": message, "type": "platform_error"}}


class FakeContext:
    """Answers every model request with `status` and `reply`, or raises `failure`."""

    def __init__(self, reply: JsonObject | None = None, status: int = 200) -> None:
        self.reply = reply if reply is not None else completion("A reply.")
        self.status = status
        self.failure: Exception | None = None
        self.requests: list[JsonObject] = []
        self.authorizations: list[str] = []
        self.reports: list[tuple[str, JsonValue]] = []
        self.clients: list[AsyncOpenAI] = []

    @property
    def activation_id(self) -> str:
        return "a1"

    def remaining_seconds(self) -> float:
        return 5.0

    async def report(self, kind: str, content: JsonValue) -> None:
        self.reports.append((kind, content))

    def llm_client(self) -> AsyncOpenAI:
        transport = httpx2.MockTransport(self._respond)
        client = AsyncOpenAI(
            base_url="http://platform.test/v1",
            api_key="grant-1",
            max_retries=0,
            http_client=httpx2.AsyncClient(transport=transport),
        )
        self.clients.append(client)
        return client

    def steps(self) -> list[JsonValue]:
        assert all(kind == "step" for kind, _ in self.reports)
        return [content for _, content in self.reports]

    def _respond(self, request: httpx2.Request) -> httpx2.Response:
        self.requests.append(json_object(decode_json(request.content.decode())))
        self.authorizations.append(request.headers["authorization"])
        if self.failure is not None:
            raise self.failure
        return httpx2.Response(self.status, json=self.reply)
