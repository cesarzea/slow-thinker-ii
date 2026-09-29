# Execution evidence inspector: specification

Displays recorded events, calls, activations and retained content for a selected run.

## Public boundary

The [public entry point](index.ts) is authoritative for exported names and signatures.

- Inspector is the feature public component.
- Evidence views follow backend identifiers to call, activation and payload projections.

## Required behavior

- Render captured content as data, never executable markup.
- Preserve missing, redacted, unavailable and omitted content states.
- Load bounded pages, abort stale reads and move focus to selected evidence so navigation remains visible.
- Present recorded facts without inventing agent reasoning or causal influence.

## Dependencies and ownership

Public API and UI modules; cross-feature selection belongs to the app.

## Acceptance criteria

- Call and payload links reveal the selected content in the visible inspector.
- Changing runs cannot display a late response from a previous run.

## Shared contracts

- [observation](../../../../docs/contracts/observation.md)
- [visual-model](../../../../docs/architecture/visual-model.md)

## Sprint additions

- [inspection-projections](../../../../docs/contracts/inspection-projections.md) defines the implemented cross-package boundary; existing supported behavior remains compatible.

## External selection and reports

The public InspectionSelection union contains call, activation and payload
identities. Inspector accepts optional `selection` while retaining credential/run
inputs. External selections reuse the existing selection reducer and focused
headings; internal evidence links continue to work independently. Re-selecting an
object requests focus again without choosing a substitute activation.

Activation and call details show component reports with their declared kind,
schema version, event sequence, source timestamp and reported provenance. Captured
payload links retain the existing missing/redacted/unavailable handling. No reports
produces an explicit unavailable-reasoning message. These reports do not become
provider attempts or inferred reasoning.

## Verification

The frontend feature/API suites pass with 119 tests and the mandatory coverage
thresholds (2026-09-29). Browser journeys verify all five catalog graphs, retained
execution/inspection, bounded rejection then acceptance, exhaustion and responsive
keyboard selection against the simulated-provider backend. Type, lint, formatting,
dead-code and dependency-boundary checks pass. Sprint-wide final verification is
coordinated separately in the shared verification record.

A focused evidence heading stays visible when asynchronous content changes the
inspector height. Visibility tracking ends on unmount and never restores focus
after the operator moves to another control.
