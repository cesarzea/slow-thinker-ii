"""Read models of a run built from its event log: the run view and pages of events."""

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from types import MappingProxyType

from slow_thinker_ii.contracts import JsonObject, JsonValue, json_value, value_at_pointer

from ._records import RecordedEvent, RunRecord, rfc3339


@dataclass(frozen=True)
class RunView:
    summary: RunRecord
    results: tuple[JsonObject, ...]  # {"node_id", "name", "payload", "at"}
    activations_by_node: Mapping[str, int]
    messages_by_connection: Mapping[str, int]  # "<from node>.<port> -> <to node>.<port>"

    def to_json(self) -> JsonObject:
        """`GET /runs/{run_id}`: the run summary plus results and counts."""
        document = self.summary.to_json()
        document["results"] = [json_value(result) for result in self.results]
        document["activations_by_node"] = dict(self.activations_by_node)
        document["messages_by_connection"] = dict(self.messages_by_connection)
        return document


@dataclass(frozen=True)
class EventPage:
    events: tuple[RecordedEvent, ...]
    last_seq: int  # of the last event returned, or `after` when none
    finished: bool  # the run is terminal and this page reaches the end of its log

    def to_json(self) -> JsonObject:
        events: list[JsonValue] = [event.to_json() for event in self.events]
        return {"events": events, "last_seq": self.last_seq, "finished": self.finished}


def run_view(summary: RunRecord, events: Iterable[RecordedEvent]) -> RunView:
    results: list[JsonObject] = []
    activations: dict[str, int] = {}
    messages: dict[str, int] = {}
    for event in events:
        if event.kind == "run.result":
            results.append(_result(event))
        elif event.kind == "activation.started":
            node = event.node_id or ""
            activations[node] = activations.get(node, 0) + 1
        elif event.kind == "message.sent":
            connection = f"{_end(event.data, 'from')} -> {_end(event.data, 'to')}"
            messages[connection] = messages.get(connection, 0) + 1
    return RunView(
        summary, tuple(results), MappingProxyType(activations), MappingProxyType(messages)
    )


def _result(event: RecordedEvent) -> JsonObject:
    return {
        "node_id": event.node_id,
        "name": event.data.get("name"),
        "payload": event.data.get("payload"),
        "at": rfc3339(event.at),
    }


def _end(data: JsonObject, key: str) -> str:
    """`<node>.<port>` of a message's `from` or `to`."""
    return f"{value_at_pointer(data, (key, 'node_id'))}.{value_at_pointer(data, (key, 'port'))}"
