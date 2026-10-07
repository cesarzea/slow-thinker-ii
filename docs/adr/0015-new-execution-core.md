# ADR 0015: Build a new execution core that reuses verified subsystems

- Status: Accepted
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR01–CR18
- Evidence: [development assessment](../archive/previous-implementation/reviews/2026-10-04-development-assessment/README.md)

## Context and problem statement

The previous implementation had no first-class node, port or connection model:
topology lived in the configuration of controller components, which only echoed a
decision the core had already taken. Model providers were instances inside each
graph, permissions were written by hand, only one run could be active, and
composition rewrote the graph around wrapper components. Five technically verified
S06 deliveries were rejected by the owner. The owner's target model (graphs of any
shape, asynchronous messages, invisible embedding, platform-level model providers,
connections as authorization) cannot be reached by reducing that code.

## Considered options

| Option | Assessment |
| --- | --- |
| Reduce and sanitise the existing core | Keeps topology in controller configuration and the per-profile stacks; reaching the target model requires the same model change as a new core |
| Rewrite everything from scratch | Discards shape-independent, well-tested subsystems: call grants, reservations before dispatch, settlement, MCP transport, the component SDK and the quality tooling |
| New core reusing verified subsystems | New graph model, engine, persistence schema and product interface; selected subsystems are carried over after review |

## Decision outcome

Build a new core on a branch from the published S03 baseline. Reuse, after review,
the shape-independent subsystems: JSON contracts, money and tariff arithmetic,
invocation grants, the MCP stdio transport and readiness checks, the component
host SDK, component installation, provider transports, the HTTP gateway pattern,
frontend transport and interface primitives, and the quality tooling. Delete the
controller components, wrapper composers, the per-graph model resource and the
legacy OpenAI model package. The previous implementation and its documentation
are archived, not published.

## Consequences

Old graph definitions and run history are not migrated; the local databases are
archived read-only. Contracts of the previous implementation are superseded by the
new [contracts](../contracts/README.md). Reused code must pass the unchanged gates
in its new context.
