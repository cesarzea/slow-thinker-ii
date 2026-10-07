# ADR 0017: Message-driven asynchronous execution

- Status: Accepted; the activation-failure policy was accepted on 2026-10-07 with S06
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR01–CR03, CR07, CR12

## Context and problem statement

Graphs must eventually take any shape, run nodes in parallel and change at runtime.
S06 needs simple semantics that do not block those goals.

## Decision outcome

Execution follows the [execution contract](../contracts/execution.md):

- A trigger starts a run by emitting its message. Each message delivered to an
  input port starts one activation of the receiving node.
- An output port connected to several inputs delivers to all of them; activations
  run concurrently up to the run's limit on running nodes. Further deliveries wait
  in the run's queue.
- A stateless component may have several activations of the same node at once.
  A stateful node rejects a delivery while it is busy.
- An embedded output component runs inside the activation, after the host
  component, and selects the port and content to emit.
- A run completes when no delivery is pending and no activation is running. It
  stops when a limit is reached or the operator stops it.
- Accepted: a failed activation stops the run with status `failed`, cancelling
  activations still running. A future option may let a graph continue on errors.

## Consequences

Joins, conversation threads, queues, shared context and runtime graph changes
remain later capabilities with clear extension points: new component kinds,
embedding positions and delivery policies. The engine is a pure asynchronous
scheduler behind ports, testable without processes.
