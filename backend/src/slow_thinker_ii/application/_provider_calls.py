"""One provider attempt, run as a task the run cancels if it ends before the provider answers."""

import asyncio
from datetime import datetime

from slow_thinker_ii.contracts import JsonObject

from ._active import ActiveCall
from ._call_record import error_body
from ._ports import Clock, LlmProvider
from ._values import LlmModel, ProviderReply

MIN_TIMEOUT_SECONDS = 0.001


async def provider_reply(
    provider: LlmProvider, call: ActiveCall, model: LlmModel, request: JsonObject, clock: Clock
) -> ProviderReply:
    """The provider's reply; 504 when the run ended first, 502 when the adapter raised."""
    timeout = max(call.remaining_seconds, MIN_TIMEOUT_SECONDS)
    task = asyncio.create_task(provider.complete(model, request, timeout))
    call.run.watch(task)
    try:
        await asyncio.wait({task})
    except asyncio.CancelledError:
        task.cancel()
        raise
    finally:
        call.run.unwatch(task)
    if task.cancelled():
        return unanswered(clock.now(), "The run ended before the provider answered.")
    error = task.exception()
    if error is not None:
        message = f"The provider adapter failed: {type(error).__name__}."
        now = clock.now()
        return ProviderReply(502, error_body(502, "provider_error", message), None, now, now)
    return task.result()


def unanswered(at: datetime, message: str) -> ProviderReply:
    """A 504 without usage: the call is settled at its reservation, as estimated."""
    return ProviderReply(504, error_body(504, "provider_timeout", message), None, at, at)
