# Browser application composition: specification

Composes access, graph selection, execution and inspection into one local operator workspace.

## Public boundary

The [public entry point](app.tsx) is authoritative for exported names and signatures.

- App is the root React component imported by main.tsx.
- The app owns cross-feature graph, run and inspection selection.

## Required behavior

- Keep credentials in memory and discard stale feature state when access changes.
- Connect features through public APIs; do not introduce imports between sibling features.
- Preserve selected experiment and run identities when opening evidence.

## Dependencies and ownership

Public api, ui and feature entry points; no direct provider or component access.

## Acceptance criteria

- Changing credentials cannot expose a stale run from the previous workspace.
- Selecting a graph or run updates the corresponding workspace coherently.

## Shared contracts

- [visual-model](../../../docs/architecture/visual-model.md)
- [module-boundaries](../../../docs/architecture/module-boundaries.md)

## Sprint additions

- [inspection-projections](../../../docs/contracts/inspection-projections.md) defines the implemented cross-package boundary; existing supported behavior remains compatible.

## Definition and evidence composition

The app loads the selected catalog revision before enabling its run inputs. A
separate saved-run graph uses the admitted definition and the execution feature's
polling observation; changing the experiment does not substitute its definition
for a saved run. Graph object selection shows configuration and a list of exact
matching activations. Activation/call selections become the inspector's public
InspectionSelection, without imports between features.

Credential reconnection remounts the execution workspace. Retained evidence stays
associated with the run explicitly selected for inspection, with that identity
visible in the inspector. A stale live projection is labeled without sending any
command or changing backend state.

## Verification

Current local gate results are recorded in the shared verification record.
The 2026-09-30 delivery preserves the module acceptance criteria above.

## Agent canvas and English delivery

Follow the approved [sprint contract](../../../docs/specification/agent-canvas-sprint.md) for presentation,
configuration provenance, identity, ownership and acceptance tests. It supersedes
earlier canvas-layer and separate activation-card presentation requirements.

## English presentation contract

The document language is English. Access, experiment selection and inspection navigation use English labels without changing selected graph, run or evidence identities.
