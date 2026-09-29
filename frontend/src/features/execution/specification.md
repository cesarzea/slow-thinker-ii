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

ExecutionPanel optionally emits ExecutionObservation through `onObservation`.
Its existing credential, graph and onInspect props remain supported. Definition
and execution reads share the selected run's polling and abort lifetime. Paging
accumulates a single boundary, rejects repeated cursors/identities and never mixes
snapshots; a fresh snapshot replaces an existing complete one only when assembled.
Projection failures retain labeled stale evidence without mutating commands.

## Verification

The frontend feature/API suites pass with 119 tests and the mandatory coverage
thresholds (2026-09-29). Browser journeys verify all five catalog graphs, retained
execution/inspection, bounded rejection then acceptance, exhaustion and responsive
keyboard selection against the simulated-provider backend. Type, lint, formatting,
dead-code and dependency-boundary checks pass. Sprint-wide final verification is
coordinated separately in the shared verification record.
