# Sequence controller: specification

Chooses the next activation in a declared finite sequence without making model calls.

## Public boundary

The [public entry point](src/slow_thinker_sequence/__init__.py) is authoritative for exported names and signatures.

- Sequence accepts declared steps and next returns a Decision from completed_nodes.
- SequenceHost exposes the controller through MCP.

## Required behavior

- Accept only an exact completed prefix of the configured sequence.
- Return the next declared step or completion; reject invalid progress.
- Keep finite Sequence semantics separate from the bounded conditional profile.

## Dependencies and ownership

Public host SDK; no provider, persistence or backend imports.

## Acceptance criteria

- Empty progress returns the first step and a complete prefix returns completion.
- Unknown or out-of-order completed steps fail explicitly.

## Shared contracts

- [graphs](../../docs/contracts/graphs.md)

## S04–S06 active delivery

Follow [the shared contract](../../docs/contracts/tools-memory.md). Implementation owner: B.

Retain ordinary finite sequence behavior. Structured authoring must configure node order through the same existing public contract.

Completion requires the shared delivery acceptance evidence; implementation alone
does not close verification. Keep existing approved contracts compatible.

## Local delivery checkpoint — 2026-10-02

S04–S06 implementation, individual/whole-system review and mandatory shared
verification are complete. The [verification record](../../docs/verification.md#provider-resource-and-workspace-delivery--2026-10-02)
is authoritative for final evidence and limitations; earlier preparation/scoped-test
statuses above describe preceding checkpoints. Owner review and hosted checks remain
separate. No implementation ticket remains for this delivery.
