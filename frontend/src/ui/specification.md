# Shared interface primitives: specification

Provides small presentation primitives and exact monetary labels for browser features.

## Public boundary

The [public entry point](index.ts) is authoritative for exported names and signatures.

- ActionButton provides a native accessible action button.
- moneyLabel formats validated decimal monetary strings and unresolved values.

## Required behavior

- Do not own domain state or perform HTTP requests.
- Do not use floating-point rounding to hide small positive costs.
- Use native interaction semantics and preserve disabled states.

## Dependencies and ownership

React and standard browser facilities; no feature imports.

## Acceptance criteria

- Positive nanodollar amounts remain visible and unresolved costs remain explicit.
- Invalid monetary strings fail rather than being displayed as a plausible amount.

## Shared contracts

- [accounting-policy](../../../docs/contracts/accounting-policy.md)

## Agent canvas and English delivery

Follow the approved [sprint contract](../../../docs/specification/agent-canvas-sprint.md) for presentation,
configuration provenance, identity, ownership and acceptance tests. It supersedes
earlier canvas-layer and separate activation-card presentation requirements.

## English presentation contract

Monetary labels and validation errors are English. Decimal precision, validation behavior and public signatures remain unchanged.

## S04–S06 active delivery

Follow [the shared contract](../../../docs/contracts/product-workspace.md). Implementation owner: C.

Provide reusable form/layout/panel presentation for the product workspace, with keyboard/focus/error/loading semantics. No provider, budget policy, transport or sibling feature dependencies.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
