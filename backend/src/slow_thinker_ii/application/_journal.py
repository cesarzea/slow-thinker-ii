"""A run's event log as the engine's `RunLog`, with the totals kept as events are recorded."""

import math

from slow_thinker_ii.accounting import format_usd, parse_usd
from slow_thinker_ii.contracts import JsonObject, JsonValue

from ._ports import Clock, RunStore
from ._records import NewEvent


class Totals:
    """Counts and model-call sums of one run, accumulated from its events."""

    def __init__(self) -> None:
        self.activations = 0
        self.messages = 0
        self.dropped = 0
        self._llm_calls = 0
        self._input_tokens = 0
        self._output_tokens = 0
        self._cost = 0

    def observe(self, kind: str, data: JsonObject) -> None:
        if kind == "activation.started":
            self.activations += 1
        elif kind == "message.sent":
            self.messages += 1
        elif kind == "message.dropped":
            self.dropped += 1
        elif kind == "llm.called":
            self._model_call(data)

    def document(self, duration_ms: int, activations: int, messages: int) -> JsonObject:
        """The `totals` of `run.finished`; input tokens include cached and cache-write tokens."""
        return {
            "duration_ms": duration_ms,
            "activations": activations,
            "messages": messages,
            "llm_calls": self._llm_calls,
            "input_tokens": self._input_tokens,
            "output_tokens": self._output_tokens,
            "cost_usd": format_usd(self._cost),
        }

    def _model_call(self, data: JsonObject) -> None:
        self._llm_calls += 1
        usage = data.get("usage")
        if isinstance(usage, dict):
            inputs = ("input", "cached_input", "cache_write")
            self._input_tokens += sum(_count(usage.get(name)) for name in inputs)
            self._output_tokens += _count(usage.get("output"))
        cost = data.get("cost_usd")
        self._cost += parse_usd(cost) if isinstance(cost, str) else 0


class RunJournal:
    """Appends a run's events with their time and elapsed milliseconds since admission."""

    def __init__(self, run_id: str, store: RunStore, clock: Clock) -> None:
        self.run_id = run_id
        self.totals = Totals()
        self.running = False  # `run.running` was recorded
        self._store = store
        self._clock = clock
        self._admitted = clock.monotonic()

    def record(
        self,
        kind: str,
        data: JsonObject,
        *,
        node_id: str | None = None,
        activation_id: str | None = None,
    ) -> None:
        self._append(kind, "observed", data, node_id, activation_id)

    def report(self, data: JsonObject, *, node_id: str, activation_id: str) -> None:
        """A component's report, recorded as reported evidence."""
        self._append("report", "reported", data, node_id, activation_id)

    def elapsed_ms(self) -> int:
        return max(0, math.floor((self._clock.monotonic() - self._admitted) * 1000))

    def _append(
        self,
        kind: str,
        evidence: str,
        data: JsonObject,
        node_id: str | None,
        activation_id: str | None,
    ) -> None:
        at, elapsed = self._clock.now(), self.elapsed_ms()
        event = NewEvent(at, elapsed, kind, evidence, node_id, activation_id, data)
        self._store.append(self.run_id, event)
        self.totals.observe(kind, data)
        self.running = self.running or kind == "run.running"


def _count(value: JsonValue) -> int:
    return value if isinstance(value, int) else 0
