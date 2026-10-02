# Execution controls: specification

Lets the operator manage saved sessions, submit runs and inspect execution state and results.

## Public boundary

The [public entry point](index.ts) is authoritative for exported names and signatures.

- ExecutionPanel composes controls for a selected graph and authenticated workspace.
- createExecutionModel constructs command and polling state around IdentityStorage.

## Required behavior

- Use durable command identities for start, stop and withdrawal recovery.
- Persist only permitted identities; do not persist credentials or prompt content in browser storage.
- Treat backend projections as authoritative and cancel stale polling on selection or lifecycle changes.

## Dependencies and ownership

Public API and UI modules; the app composes this feature with graph-view and inspector.

## Acceptance criteria

- An uncertain start can be recovered without dispatching a duplicate run.
- Completed, failed and stopped runs retain inspectable results and budget state.

## Shared contracts

- [operator-api](../../../../docs/contracts/operator-api.md)
- [visual-model](../../../../docs/architecture/visual-model.md)

## Sprint additions

- [inspection-projections](../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package boundary; existing supported behavior remains compatible.

## Schema input and shared projection lifetime

StartControls uses the selected definition's input schema. Primitive object
properties retain a labeled form; other supported shapes inside an object use JSON input. Root strings, arrays and
null are rejected because the operator wire contract requires a JSON object.
Ajv2020 validates either representation with no remote schema fetching. Invalid
or unsupported schemas fail explicitly. The command boundary also validates input;
its existing string argument remains a compatibility adapter for `{problem: text}`.
The app withholds Start until the exact definition is available.

For S03, the app also supplies `inputUnavailable` while a definition draft is dirty
or a confirmed saved revision awaits selection. Start exposes an accessible
explanation; Stop and retained-run controls remain independent of that gate.

ExecutionPanel optionally emits ExecutionObservation through `onObservation`.
Its existing credential, graph and onInspect props remain supported. Definition
and execution reads share the selected run's polling and abort lifetime. Paging
accumulates a single boundary, rejects repeated cursors/identities and never mixes
snapshots; a fresh snapshot replaces an existing complete one only when assembled.
Projection failures retain labeled stale evidence without mutating commands.

## Verification

Current local gate results are recorded in the shared verification record.
The 2026-09-30 delivery preserves the module acceptance criteria above.

## Agent canvas and English delivery

Follow the approved [sprint contract](../../../../docs/specification/agent-canvas-sprint.md) for presentation,
configuration provenance, identity, ownership and acceptance tests. It supersedes
earlier canvas-layer and separate activation-card presentation requirements.

## English presentation contract

Product-authored session, start, stop, history, budget and recovery text is English. Input schema titles, user input, receipt reasons and recorded results are rendered without translation. Command identities, polling and recovery behavior remain unchanged.
