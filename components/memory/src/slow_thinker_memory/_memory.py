"""The node's latest exchanges, kept in this host's process for the run."""

from dataclasses import dataclass

from slow_thinker_host import Context, JsonValue, encode_json


@dataclass(frozen=True)
class Exchange:
    received: JsonValue
    replied: JsonValue


def _text(value: JsonValue) -> str:
    return value if isinstance(value, str) else encode_json(value)


def with_history(history: list[Exchange], message: JsonValue) -> JsonValue:
    """The message as the node receives it: unchanged without history, else a transcript."""
    if not history:
        return message
    lines = ["Conversation so far:"]
    for exchange in history:
        lines.append(f"You received: {_text(exchange.received)}")
        lines.append(f"You replied: {_text(exchange.replied)}")
    lines.extend(["", "New message:", _text(message)])
    return "\n".join(lines)


class Memory:
    """Recall adds the latest exchanges to the message; remember keeps each new exchange."""

    def __init__(self, max_exchanges: int) -> None:
        self._max = max_exchanges
        self._exchanges: list[Exchange] = []

    async def recall(self, message: JsonValue, context: Context) -> JsonValue:
        del context
        return with_history(self._exchanges, message)

    async def remember(self, received: JsonValue, replied: JsonValue, context: Context) -> None:
        del context
        self._exchanges = [*self._exchanges, Exchange(received, replied)][-self._max :]
