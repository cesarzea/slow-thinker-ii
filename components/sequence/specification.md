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
