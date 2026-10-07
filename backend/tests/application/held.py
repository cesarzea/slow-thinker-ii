"""Runs whose first LLM Call is held, so tests can call the gateway with its live grant."""

from slow_thinker_ii.application import GatewayReply
from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from slow_thinker_ii.engine import CallContext
from support.examples import J1, LUNA
from support.hosts import Gate
from support.platform import Platform
from support.waiting import until


async def held_call(platform: Platform, document: JsonObject | str = J1) -> CallContext:
    """Starts `document` and returns the context of its first, held, LLM Call activation."""
    platform.hold = Gate()
    known = len(platform.hosts)
    await platform.started(document)
    await until(lambda: len(platform.hosts) > known and bool(platform.hosts[known].contexts))
    return platform.hosts[known].contexts[0]


async def stopped(platform: Platform, context: CallContext) -> None:
    """Stops the held run and waits until it has ended and been cleaned up."""
    platform.runs.stop(context.run_id)
    await platform.finish(context.run_id)


def body(model: str = LUNA, /, **fields: JsonValue) -> str:
    """A Chat Completions request for `model` with one user message and `fields`."""
    document: JsonObject = {"model": model, "messages": [{"role": "user", "content": "Hi"}]}
    return encode_json({**document, **fields})


def error_code(reply: GatewayReply) -> tuple[int, JsonValue]:
    error = reply.body["error"]
    assert isinstance(error, dict)
    return reply.status, error["code"]


def calls(platform: Platform, context: CallContext) -> list[JsonObject]:
    """The `llm.called` data recorded for the run of `context`."""
    return [event.data for event in platform.run_store.of(context.run_id, "llm.called")]
