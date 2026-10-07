# ADR 0013 — Separate authoring, immutable versions and execution views

> **Superseded on 2026-10-04** by [ADR 0016](0016-graph-document-model.md). The record below is retained unchanged.


| Decision record | Value                                                                           |
| --------------- | ------------------------------------------------------------------------------- |
| Date            | 2026-10-02                                                                      |
| Status          | Owner-authorized implementation; locally verified; usability acceptance pending |
| Owner           | Cesar Zea                                                                       |
| Context         | [S06 usability review](../archive/previous-implementation/reviews/2026-10-02-ui-usability/README.md)            |

## Context and decision drivers

The current canvas and configuration forms can refer to different selections and
different draft states. Local field buffers escape global dirty guards. A usable
workspace must preserve arbitrary component configuration, immutable run evidence
and exact JSON numbers while supporting later comparison and nested graphs.

Drivers are coherent editing, extensibility, reproducibility, bounded scope and
independent package assignments under the existing engineering rules.

## Considered options

1. Move existing editors into a new layout without changing their state contracts.
   Small initial change, but leaves selection, unsaved-field and revision defects.
2. Give each screen its own parsed mutable graph and reconcile them on Save.
   Simple local forms, but conflicting edits, numeric loss and cross-screen recovery.
3. Retain canonical source and backend patches, with one controlled authoring state,
   separate immutable-version browsing and independently retained execution views.

## Proposed decision

Use option 3. App owns navigation and selection; definition-editor owns the working
source, field buffers and save recovery. Features consume validated data/callbacks
through public entry points. Graph geometry never becomes runtime graph state.
Backend read models provide complete experiment collection/history and bounded
exact definition comparison. Saved runs always resolve their admitted snapshots.

Enhance generic forms with optional validated presentation metadata. Existing
immutable component descriptors remain unchanged; exact-version compatibility
profiles may supply presentation for bundled types. Real accounts and credits stay
deferred; explicitly illustrative UI data never participates in accounting.

## Consequences

- Selection and pending edits become shared contracts, rather than local widget
  choices. This requires correcting existing form/editor code, not only CSS.
- History needs additive read APIs and a nullable save-time migration. Legacy
  timestamps/authors cannot be reconstructed; absence remains visible.
- New public feature interfaces permit independent delivery without sibling imports.
- Generic fallback preserves unknown types. Metadata alone cannot add runtime
  resource use, graph nesting or new execution profiles.
- Later evaluation and graph nesting can extend separate views and identities;
  this does not promise that their future interaction design is already complete.

## Confirmation

Verify [W01–W14](../archive/previous-implementation/specification/s06-workspace-redesign.md#acceptance-matrix), including
late patch/save replies, invalid buffered fields, shared instances, historical run
isolation, paged versions and large exact numbers. Preserve all existing quality
gates. A prepared contract is not evidence of successful implementation or testing.

## Implementation checkpoint — 2026-10-03

The owner activated S06-UX implementation against this design. The unchanged
mandatory verification and local demonstration now pass, as recorded in the
[S06 report](../archive/previous-implementation/progress/sprint-06-status-report.md). This replaces the preparation
status recorded on 2026-10-02; it does not claim owner usability acceptance or a
published release. The decision and runtime/accounting boundaries are unchanged.
