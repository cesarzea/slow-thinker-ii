"""Messages created from an activation's emissions: one delivery per connection, in order."""

from slow_thinker_ii.contracts import JsonObject, JsonValue, encode_json
from slow_thinker_ii.graphs import RunPlan

from ._ports import CallFailure, Emission, RunLog
from ._state import Activation, Delivery, Port, RunState

MAX_PAYLOAD_BYTES = 262_144  # serialized payload limit of the execution contract


class Emitter:
    def __init__(self, plan: RunPlan, log: RunLog, state: RunState) -> None:
        self._plan = plan
        self._log = log
        self._state = state

    def emit(self, activation: Activation, emissions: tuple[Emission, ...]) -> list[JsonValue]:
        """Records and queues the messages of each emission; returns the `emitted` list."""
        emitted: list[JsonValue] = []
        for emission in emissions:
            message_ids = self._deliver(activation, emission)
            emitted.append({"port": emission.port, "message_ids": message_ids})
        return emitted

    def _deliver(self, activation: Activation, emission: Emission) -> list[JsonValue]:
        source = (activation.node.id, emission.port)
        targets = self._plan.routes.get(source, ())
        if not targets:
            data: JsonObject = {
                "from": endpoint(source),
                "reason": "no_connection",
                "payload": emission.payload,
            }
            self._log.record(
                "message.discarded", data, node_id=source[0], activation_id=activation.id
            )
        return [self._send(activation, source, target, emission.payload) for target in targets]

    def _send(self, activation: Activation, source: Port, target: Port, payload: JsonValue) -> str:
        message_id = self._state.next_message_id()
        data: JsonObject = {
            "message_id": message_id,
            "from": endpoint(source),
            "to": endpoint(target),
            "payload": payload,
        }
        self._log.record("message.sent", data, node_id=source[0], activation_id=activation.id)
        self._state.queue.append(Delivery(message_id, source, target, payload))
        return message_id


def oversized(emissions: tuple[Emission, ...]) -> CallFailure | None:
    """A `payload_too_large` failure for the first payload above the contract's limit."""
    for emission in emissions:
        size = len(encode_json(emission.payload).encode("utf-8"))
        if size > MAX_PAYLOAD_BYTES:
            message = (
                f'The output "{emission.port}" carries {size} bytes; '
                f"messages are limited to {MAX_PAYLOAD_BYTES} bytes."
            )
            return CallFailure("payload_too_large", message)
    return None


def endpoint(port: Port) -> JsonObject:
    """The `from` or `to` object of a message record."""
    return {"node_id": port[0], "port": port[1]}
