# ADR 0021: Supervision and recording by default

- Status: Accepted
- Recorded: 2026-10-04
- Decision-maker: Cesar Zea
- Requirements: CR02, CR11, CR13, CR14

## Context and problem statement

The platform's purpose is to analyse what happened inside a run. The owner
requires every call to be supervised and recorded by default, with a pass-through
mode possibly added later, and lets each component decide what internal activity
to report.

## Decision outcome

The platform records an append-only event log per run: messages, activations,
service calls with exact request, reply, tokens and cost, embedded component calls,
component reports and the run's status changes. Each event carries its evidence
class: observed by the platform, or reported by a component. See the
[recording contract](../contracts/recording.md). Predefined components report their
internal steps.

## Consequences

Activity views and later analysis read the same log. Payloads are size-bounded
and credentials are redacted. A future pass-through mode must be an explicit run
setting and must still record that it was used.
