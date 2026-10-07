"""A scripted `LlmProvider`: replies per catalog entry, deterministic usage, kept requests."""

import math
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from slow_thinker_ii.accounting import Usage
from slow_thinker_ii.application import LlmModel, ProviderReply
from slow_thinker_ii.contracts import JsonObject, encode_json

from .clock import FakeClock
from .hosts import Gate

type Step = Callable[[JsonObject, datetime], ProviderReply]


@dataclass(frozen=True)
class ProviderRequest:
    llm: str
    request: JsonObject
    timeout_s: float


def reply(content: str, usage: Usage | None = None, *, measured: bool = True) -> Step:
    """A 200 Chat Completions reply; usage is `usage`, or bytes ÷ 4 when `measured`."""

    def step(request: JsonObject, at: datetime) -> ProviderReply:
        counted = usage or _measured(request, content)
        body: JsonObject = {
            "id": "chatcmpl-scripted",
            "object": "chat.completion",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": "stop",
                }
            ],
        }
        return ProviderReply(200, body, counted if measured else None, at, at)

    return step


def failure(status: int, code: str, message: str) -> Step:
    """A provider error: 502 `provider_error` or 504 `provider_timeout`, without usage."""

    def step(_request: JsonObject, at: datetime) -> ProviderReply:
        body: JsonObject = {"error": {"code": code, "message": message, "type": "provider_error"}}
        return ProviderReply(status, body, None, at, at)

    return step


def raising(error: Exception) -> Step:
    """A provider adapter that fails with `error` instead of replying."""

    def step(_request: JsonObject, _at: datetime) -> ProviderReply:
        raise error

    return step


class ScriptedProvider:
    """`LlmProvider` fake. Each entry's steps answer in order and the last repeats; without
    steps it answers `Simulated reply to: <last user message>`. `gate` holds every call."""

    def __init__(self, clock: FakeClock, steps: Mapping[str, Sequence[Step]] | None = None) -> None:
        self.requests: list[ProviderRequest] = []
        self.gate: Gate | None = None
        self._clock = clock
        self._steps = {llm: list(sequence) for llm, sequence in (steps or {}).items()}

    async def complete(
        self, model: LlmModel, request: JsonObject, timeout_s: float
    ) -> ProviderReply:
        self.requests.append(ProviderRequest(model.settings.id, request, timeout_s))
        if self.gate is not None:
            await self.gate.wait()
        steps = self._steps.get(model.settings.id) or [reply(_echo(request))]
        step = steps.pop(0) if len(steps) > 1 else steps[0]
        return step(request, self._clock.now())


def _echo(request: JsonObject) -> str:
    messages = request.get("messages")
    last = messages[-1] if isinstance(messages, list) and messages else None
    content = last.get("content") if isinstance(last, dict) else None
    return f"Simulated reply to: {str(content)[:200]}"


def _measured(request: JsonObject, content: str) -> Usage:
    sent = math.ceil(len(encode_json(request).encode()) / 4)
    return Usage(sent, 0, 0, math.ceil(len(content.encode()) / 4))
