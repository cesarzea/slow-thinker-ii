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

Current local gate results are recorded in the shared verification record.
The 2026-09-30 delivery preserves the module acceptance criteria above.

## Agent canvas and English delivery

Follow the approved [sprint contract](../../../docs/specification/agent-canvas-sprint.md) for presentation,
configuration provenance, identity, ownership and acceptance tests. It supersedes
earlier canvas-layer and separate activation-card presentation requirements.

## English presentation contract

`GraphDetail.execution` is an optional JSON object. Catalog details may omit it; `OperatorClient.definition` still requires it in saved-definition responses. Validation preserves this metadata without altering backend or wire contracts. Client-authored validation and transport messages are English; server evidence and protocol values remain unchanged.
