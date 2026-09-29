# Browser API client: specification

Provides typed, validated HTTP access to catalog, operator commands and execution evidence.

## Public boundary

The [public entry point](index.ts) is authoritative for exported names and signatures.

- loadGraphs returns validated GraphSummary values.
- OperatorClient exposes workspace, run, history, result and command operations.
- events, call, payload and activation fetch bounded inspection projections.
- Public response types are derived from the module validation schemas.

## Required behavior

- Validate untrusted responses before exposing them to UI features.
- Support aborted reads and bounded failures; keep credentials out of durable browser storage.
- Recover uncertain commands through their identity rather than blindly resubmitting effects.

## Dependencies and ownership

Browser fetch and Zod schemas; features use index.ts rather than private schemas.

## Acceptance criteria

- Malformed server data produces a visible failure rather than partially trusted state.
- Paging and cancellation cannot combine evidence from different selected runs.

## Shared contracts

- [operator-api](../../../docs/contracts/operator-api.md)

## Sprint additions

- [inspection-projections](../../../docs/contracts/inspection-projections.md) defines the implemented cross-package boundary; existing supported behavior remains compatible.

## Graph and execution projections

`OperatorClient.graph(id, revision, signal)` validates an exact catalog definition;
`definition(run, signal)` validates the saved definition envelope and returns its
GraphDetail fields. `execution(run, signal, cursor?)` validates a bounded page.
The public records are GraphDetail, GraphStructure, ComponentView, PlannedNodeView,
RelationshipView, ExecutionPage, ActivationView and CommunicationView.

Definitions are checked against the canonical graph JSON schema with Ajv2020.
Structural identities, relationship endpoints and containment are checked before
exposure. Reports retain `reported` provenance and nullable captured payloads.
Catalog summaries and detail reports accept omitted additive fields for existing
consumers; the graph-detail and execution endpoints require their full contract.

## Verification

The frontend feature/API suites pass with 119 tests and the mandatory coverage
thresholds (2026-09-29). Browser journeys verify all five catalog graphs, retained
execution/inspection, bounded rejection then acceptance, exhaustion and responsive
keyboard selection against the simulated-provider backend. Type, lint, formatting,
dead-code and dependency-boundary checks pass. Sprint-wide final verification is
coordinated separately in the shared verification record.
