# Memory component: specification

Package `slow-thinker-memory`, import `slow_thinker_memory`, declaration
`component.json` shipped as package data, equal to the contract
[example](../../docs/contracts/examples/memory.component.json). Entry point:
`python -m slow_thinker_memory <bootstrap>`. Placement: `memory` only; stateful. It
imports the [host SDK](../host/specification.md) only. See
[ADR 0026](../../docs/adr/0026-memory-position.md).

## Public interface

```text
@dataclass(frozen=True)
class Exchange:
    received: JsonValue
    replied: JsonValue

def with_history(history: list[Exchange], message: JsonValue) -> JsonValue

class Memory:                                              # MemoryHandler
    def __init__(self, max_exchanges: int) -> None
    async def recall(self, message: JsonValue, context: Context) -> JsonValue
    async def remember(self, received: JsonValue, replied: JsonValue, context: Context) -> None

def main(arguments: Sequence[str], serve: Serve = run_host) -> None
```

## Behaviour

- At startup the host checks the bootstrap against the declaration and reads
  `max_exchanges`, a whole number from 1 to 100; otherwise it stops before readiness
  with exit status 1, printing `Memory startup failed: <reason>`.
- `remember(received, replied)` keeps the exchange, dropping the oldest beyond
  `max_exchanges`. The exchanges live in the host's process, so they last for the run.
- `recall(message)` returns the message unchanged while nothing is kept. Otherwise it
  returns text: `Conversation so far:`, then for each kept exchange `You received: …`
  and `You replied: …`, a blank line, `New message:` and the message. Values that are
  not strings are written as compact JSON.
- It neither reports nor calls the LLM service. It is served as stateful, one call at a
  time, which makes its node stateful too: until input queues exist, a message that
  reaches the node while it is busy fails its activation with `node_busy`, and the run
  with it.

## Acceptance

Tests cover recall and remember with and without history, the limit, structured
values, the entry point and its startup failures, an end-to-end run of the module as a
process over stdio, and the declaration's equality with the contract example.
