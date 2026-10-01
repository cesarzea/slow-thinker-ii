# ADR 0002: Mediate managed interactions through the platform

- Status: Accepted
- Recorded: 2026-09-27
- Decision-maker: Cesar Zea
- Requirements: R05–R06, R09, R11–R15

## Context and problem statement

Direct component-to-component calls would bypass the observation and execution controls required to analyze collaboration and enforce budgets. The owner explicitly requires the platform to sit between managed callers and targets.

## Decision drivers

Complete managed-call attribution, graph-scoped access, spending admission, cancellation, and component autonomy over message content.

## Considered options

| Option | Benefit | Cost or limitation |
| --- | --- | --- |
| Platform mediation | One authority for access, limits and evidence | Routing overhead and a central availability dependency |
| Direct calls with reporting | Fewer routing steps | Missing reports defeat central guarantees |
| Peer-to-peer authorization and accounting | Distributed operation | Coordination complexity exceeds initial scope |

## Decision outcome

Managed components expose MCP capabilities to the platform. The platform exposes only authorized capabilities to consumers and records dispatch and outcome. The same policy applies to model resources and compatibility APIs. An agent remains responsible for selecting its own inputs and context.

Internal instrumentation is optional except information required for managed spending authorization and accounting. A self-reported caller name or tool annotation does not authorize access.

## Consequences

Nested calls must remain serviceable while parent calls wait. The platform must record errors and rejected requests as well as successful work. Trace storage is not automatically a resource visible to agents.

The initial trusted-component contract does not physically prevent arbitrary code from using the network. Strong containment requires a later isolation design; this limitation must not be hidden behind the word “proxy.”

## Confirmation

QA03 verifies discovery and invocation filtering. QA06–QA09 verify spending controls. QA14 checks that alternate entry interfaces cannot bypass them. The runtime scenario exercises nested model requests without deadlock.
