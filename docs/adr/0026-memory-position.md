# 0026. Memory as an embedded component position

| Decision control | Value                                                        |
| ---------------- | ------------------------------------------------------------ |
| Status           | Accepted                                                     |
| Date             | 2026-10-05                                                   |
| Deciders         | Cesar Zea (owner)                                            |
| Amends           | [ADR 0004](0004-component-packaging.md), [ADR 0007](0007-mcp-profile.md), [ADR 0023](0023-container-ready-component-boundary.md) |

## Context and problem

The owner asked for agents with memory that still receive only the previous node's
output, and required that components and platform stay absolutely encapsulated: the
platform must not contain a memory's logic, and the agent's component must not know
about memory. A first in-engine memory was rejected for that reason.

## Decision

- A node may embed a component at a new position, `memory`, beside an `output`
  component. Its declaration lists the `memory` placement.
- A memory host serves two operations of the component protocol: `recall`, which
  returns what the node receives instead of the delivered message, and `remember`,
  which receives the delivered message and each reply. The platform calls `recall`
  before `activate` and `remember` after it, before any output component.
- The platform knows only these operations. How a memory keeps exchanges, for how long
  and how it adds them to a message belongs to the memory component, which runs in its
  own process like any package.
- The first memory, `memory@1.0.0`, keeps a run's latest exchanges in its process and
  adds them to each message as a transcript. Persistent memories, such as mem0, are
  other components with the same two operations.

## Consequences

- Every component package was rebuilt, because the host SDK now serves the `memory`
  position; installations need new resolutions.
- A memory is stateful, so its node takes one activation at a time. Until input queues
  exist (S14), a message that reaches the node while it is still handling another
  fails its activation with `node_busy`, and the run with it; graphs that feed such a
  node from parallel branches cannot use memory yet.
- History reaches the model as text inside the message, not as chat turns; a memory
  that needs turns would need a different contract.
