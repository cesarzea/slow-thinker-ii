# ADR 0018: Authorization derived from connections and declared uses

- Status: Accepted
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR02, CR05, CR06
- Refines: [ADR 0002](0002-platform-mediation.md)

## Context and problem statement

The previous graph format required users to list permissions separately from the
bindings and routes they had already drawn. The owner stated (translated) that
connections define what may call what, because nothing calls anything directly,
and that users therefore never see permissions.

## Decision outcome

The platform derives every authorization from the graph and from component
declarations. A connection authorizes delivery from one port to another. A
component's declared service use, together with the node configuration that
selects a service entry, authorizes calls to that entry only; a node configured
with one LLM cannot call another. Platform policies, such as budgets and limits,
may further restrict any call. Each invocation receives a short-lived grant that
identifies the run, node and activation; payload contents never assert identity.

## Consequences

Ordinary configuration contains no permission concept. Authorization failures are
recorded like any other rejected call. Tools, resources and agent-to-agent calls
added later follow the same rule: assigning them is the authorization.
